from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from .models import MembershipPlan, MembershipOrder, UserMembership
from .serializers import (
    MembershipPlanSerializer, CreateMembershipPlanSerializer,
    CreateMembershipOrderSerializer, MembershipOrderSerializer,
    UserMembershipSerializer
)
from rest_framework.permissions import AllowAny
from .services.alipay_service import AlipayService
import logging

logger = logging.getLogger(__name__)

class MembershipPlanListView(generics.ListAPIView):
    """获取会员套餐列表"""
    queryset = MembershipPlan.objects.filter(is_active=True)
    serializer_class = MembershipPlanSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # 可以添加筛选逻辑
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        return queryset


class CreateMembershipPlanView(generics.CreateAPIView):
    """创建会员套餐（管理员功能）"""
    queryset = MembershipPlan.objects.all()
    serializer_class = CreateMembershipPlanSerializer
    permission_classes = [IsAdminUser]


class CreateMembershipOrderView(APIView):
    """创建会员订单"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateMembershipOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan_id = serializer.validated_data['plan_id']
        payment_method = serializer.validated_data['payment_method']

        try:
            plan = MembershipPlan.objects.get(id=plan_id, is_active=True)
        except MembershipPlan.DoesNotExist:
            return Response(
                {"detail": "套餐不存在或已下架"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建订单
        order = MembershipOrder.objects.create(
            user=request.user,
            plan=plan,
            amount=plan.price,
            payment_method=payment_method
        )

        # 根据支付方式生成支付信息
        if payment_method == 'alipay':
            alipay_service = AlipayService()
            payment_info = alipay_service.create_payment(
                order=order,
                return_url=request.build_absolute_uri('http://127.0.0.1:8000/api/membership/payment-result/')
            )

            response_data = {
                "order": MembershipOrderSerializer(order).data,
                "payment_info": payment_info
            }
        else:
            response_data = {
                "order": MembershipOrderSerializer(order).data,
                "message": "暂不支持该支付方式"
            }

        return Response(response_data, status=status.HTTP_201_CREATED)


class MembershipOrderListView(generics.ListAPIView):
    """获取用户订单列表"""
    serializer_class = MembershipOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MembershipOrder.objects.filter(user=self.request.user)


class MembershipOrderDetailView(generics.RetrieveAPIView):
    """获取订单详情"""
    serializer_class = MembershipOrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'out_trade_no'

    def get_queryset(self):
        return MembershipOrder.objects.filter(user=self.request.user)


class UserMembershipInfoView(APIView):
    """获取用户会员信息"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            membership = UserMembership.objects.get(user=request.user)
            serializer = UserMembershipSerializer(membership)
        except UserMembership.DoesNotExist:
            # 如果用户没有会员信息，返回默认数据
            serializer = UserMembershipSerializer({
                'plan': None,
                'is_active': False,
                'started_at': None,
                'expires_at': None,
                'total_orders': 0,
                'total_spent': 0
            })

        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class AlipayNotifyView(APIView):
    """支付宝异步通知处理"""
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            data = request.POST.dict()
            print(f"收到支付宝回调数据: {data}")

            # 检查必要字段
            out_trade_no = data.get('out_trade_no')
            if not out_trade_no:
                print("错误: 缺少 out_trade_no")
                return HttpResponse('fail')

            # 检查订单是否存在
            from .models import MembershipOrder
            try:
                order = MembershipOrder.objects.get(out_trade_no=out_trade_no)
                print(f"找到订单: {order.out_trade_no}, 状态: {order.status}")
            except MembershipOrder.DoesNotExist:
                print(f"错误: 订单不存在 - {out_trade_no}")
                return HttpResponse('fail')

            # 处理支付回调
            alipay_service = AlipayService()
            result = alipay_service.process_notify(data)

            print(f"处理结果: {result}")

            if result.get('success'):
                return HttpResponse('success')
            else:
                print(f"处理失败: {result.get('message')}")
                return HttpResponse('fail')

        except Exception as e:
            print(f"支付宝回调处理异常: {e}")
            import traceback
            traceback.print_exc()
            return HttpResponse('fail')

    def get(self, request):
        return HttpResponse('AlipayNotifyView is working')


class PaymentResultView(APIView):
    """支付结果页面（同步回调）"""
    permission_classes = [AllowAny]

    def get(self, request):
        out_trade_no = request.GET.get('out_trade_no')

        if out_trade_no:
            try:
                order = MembershipOrder.objects.get(out_trade_no=out_trade_no)

                # 检查订单状态，如果支付成功则重定向到前端成功页面
                if order.status == 'paid':
                    return HttpResponseRedirect('http://127.0.0.1:5173/profile?payment=success')
                else:
                    return HttpResponseRedirect('http://127.0.0.1:5173/profile?payment=failed')

            except MembershipOrder.DoesNotExist:
                return HttpResponseRedirect('http://127.0.0.1:5173/profile?payment=error')

        return HttpResponseRedirect('http://127.0.0.1:5173/profile?payment=error')