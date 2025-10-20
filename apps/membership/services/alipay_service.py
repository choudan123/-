from django.conf import settings
from django.utils import timezone
from alipay import AliPay
from ..models import MembershipOrder, PaymentCallback, UserMembership


class AlipayService:
    def __init__(self):
        self.alipay = AliPay(
            appid=settings.ALIPAY_CONFIG['app_id'],
            app_notify_url=settings.ALIPAY_CONFIG['notify_url'],
            app_private_key_string=settings.ALIPAY_CONFIG['app_private_key'],
            alipay_public_key_string=settings.ALIPAY_CONFIG['alipay_public_key'],
            sign_type=settings.ALIPAY_CONFIG['sign_type'],
            debug=settings.ALIPAY_CONFIG['debug']
        )

    def create_payment(self, order: MembershipOrder, return_url: str = None):
        """创建支付订单"""
        order_data = {
            "out_trade_no": order.out_trade_no,
            "total_amount": str(order.amount),
            "subject": f"购买会员套餐 - {order.plan.name}",
            "body": f"用户 {order.user.username} 购买 {order.plan.name}",
            "timeout_express": "15m",  # 15分钟过期
        }

        if return_url:
            order_data["return_url"] = return_url

        # 生成支付URL（用于PC端）
        pay_url = self.alipay.api_alipay_trade_page_pay(**order_data)

        # 生成支付字符串（用于移动端）
        pay_string = self.alipay.api_alipay_trade_app_pay(**order_data)

        return {
            "pay_url": f"{settings.ALIPAY_CONFIG['gateway_url']}?{pay_url}",
            "pay_string": pay_string,
            "order_data": order_data
        }

    def verify_notify(self, data):
        """验证支付宝回调通知"""
        try:
            # 不要修改原始数据，创建副本
            data_copy = data.copy()
            if 'sign' not in data_copy:
                print("警告: 回调数据中缺少sign字段")
                return False

            signature = data_copy.pop("sign")
            result = self.alipay.verify(data_copy, signature)
            print(f"签名验证结果: {result}")
            return result
        except Exception as e:
            print(f"签名验证异常: {e}")
            return False

    def process_notify(self, data):
        """处理支付回调通知"""
        try:
            print(f"开始处理支付回调: {data}")

            # 记录回调
            callback = PaymentCallback.objects.create(
                out_trade_no=data.get('out_trade_no', ''),
                trade_no=data.get('trade_no', ''),
                callback_data=data
            )
            print(f"回调记录已创建: {callback.id}")

            # 验证签名
            if not self.verify_notify(data):
                print("签名验证失败")
                return {"success": False, "message": "签名验证失败"}

            # 获取订单
            try:
                order = MembershipOrder.objects.get(out_trade_no=data['out_trade_no'])
                print(f"找到订单: {order.out_trade_no}, 当前状态: {order.status}")
            except MembershipOrder.DoesNotExist:
                print(f"订单不存在: {data.get('out_trade_no')}")
                return {"success": False, "message": "订单不存在"}

            # 检查订单状态
            if order.status != 'pending':
                print(f"订单已处理，当前状态: {order.status}")
                return {"success": True, "message": "订单已处理"}

            # 检查交易状态
            trade_status = data.get('trade_status')
            print(f"交易状态: {trade_status}")

            if trade_status == 'TRADE_SUCCESS':
                # 更新订单状态
                order.status = 'paid'
                order.trade_no = data.get('trade_no')
                order.paid_at = timezone.now()
                order.alipay_response = data
                order.save()
                print(f"订单状态已更新为 paid")

                # 激活会员
                print("开始激活会员...")
                self._activate_membership(order)
                print("会员激活完成")

                # 标记回调已处理
                callback.processed = True
                callback.save()

                return {"success": True, "message": "支付成功"}
            else:
                print(f"交易状态异常: {trade_status}")
                return {"success": False, "message": f"交易状态异常: {trade_status}"}

        except Exception as e:
            print(f"处理异常: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "message": f"处理失败: {str(e)}"}

    def _activate_membership(self, order: MembershipOrder):
        """激活用户会员"""
        user = order.user
        plan = order.plan

        # 获取或创建用户会员信息
        membership, created = UserMembership.objects.get_or_create(
            user=user,
            defaults={
                'plan': plan,
                'is_active': True,
            }
        )

        # 更新会员信息
        membership.plan = plan
        membership.extend_membership(plan.duration_days)

        # 更新统计信息
        membership.total_orders += 1
        membership.total_spent += order.amount
        membership.save()

        # 更新用户模型的会员到期时间（如果用户模型有这个字段）
        if hasattr(user, 'membership_expires_at'):
            user.membership_expires_at = membership.expires_at
            user.save(update_fields=['membership_expires_at'])

    def query_order(self, out_trade_no):
        """查询订单支付状态"""
        result = self.alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
        return result