from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid


class MembershipPlan(models.Model):
    """会员套餐计划"""
    PLAN_TYPES = (
        ('monthly', '月度会员'),
        ('quarterly', '季度会员'),
        ('yearly', '年度会员'),
        ('lifetime', '终身会员'),
    )

    name = models.CharField(max_length=100, verbose_name="套餐名称")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, verbose_name="套餐类型")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="原价")
    duration_days = models.IntegerField(verbose_name="有效期天数")
    description = models.TextField(blank=True, verbose_name="套餐描述")
    features = models.JSONField(default=list, verbose_name="套餐特性列表")  # ["无限海报生成", "高清输出", "优先支持"]

    # 海报生成相关权益
    poster_quota = models.IntegerField(default=-1, verbose_name="海报生成配额(-1表示无限)")
    max_image_size = models.CharField(max_length=20, default="4K", verbose_name="最大图片尺寸")
    priority_generation = models.BooleanField(default=False, verbose_name="优先生成")

    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    is_featured = models.BooleanField(default=False, verbose_name="是否推荐")
    sort_order = models.IntegerField(default=0, verbose_name="排序")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'price']
        verbose_name = "会员套餐"
        verbose_name_plural = "会员套餐"

    def __str__(self):
        return f"{self.name} - ¥{self.price}"

    @property
    def discount_percentage(self):
        """折扣百分比"""
        if self.original_price and self.original_price > self.price:
            return int((1 - self.price / self.original_price) * 100)
        return 0


class MembershipOrder(models.Model):
    """会员订单"""
    ORDER_STATUS = (
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('expired', '已过期'),
        ('cancelled', '已取消'),
        ('refunded', '已退款'),
    )

    PAYMENT_METHODS = (
        ('alipay', '支付宝'),
        ('wechat', '微信支付'),
        ('balance', '余额支付'),
    )

    out_trade_no = models.CharField(max_length=64, unique=True, verbose_name="商户订单号")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    plan = models.ForeignKey(MembershipPlan, on_delete=models.CASCADE, verbose_name="会员套餐")

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="订单金额")
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending', verbose_name="订单状态")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="支付方式")

    # 支付宝相关字段
    trade_no = models.CharField(max_length=64, blank=True, verbose_name="支付宝交易号")
    alipay_response = models.JSONField(default=dict, blank=True, verbose_name="支付宝响应数据")

    expires_at = models.DateTimeField(verbose_name="订单过期时间")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "会员订单"
        verbose_name_plural = "会员订单"

    def __str__(self):
        return f"订单{self.out_trade_no} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.out_trade_no:
            self.out_trade_no = self.generate_order_no()
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=15)  # 15分钟过期
        super().save(*args, **kwargs)

    @staticmethod
    def generate_order_no():
        """生成订单号"""
        return f"MB{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"

    @property
    def is_expired(self):
        """是否过期"""
        return timezone.now() > self.expires_at and self.status == 'pending'


class UserMembership(models.Model):
    """用户会员信息"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='membership_info',
        verbose_name="用户"
    )
    plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="当前套餐")

    is_active = models.BooleanField(default=False, verbose_name="会员是否有效")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="到期时间")

    # 使用统计
    total_orders = models.IntegerField(default=0, verbose_name="总订单数")
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'),
                                      verbose_name="总消费金额")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "用户会员信息"
        verbose_name_plural = "用户会员信息"

    def __str__(self):
        return f"{self.user.username} - 会员信息"

    @property
    def is_expired(self):
        """会员是否过期"""
        if not self.expires_at:
            return True
        return timezone.now() > self.expires_at

    def extend_membership(self, days):
        """延长会员期限"""
        now = timezone.now()
        if self.expires_at and self.expires_at > now:
            # 如果还未过期，在原到期时间基础上延长
            self.expires_at += timezone.timedelta(days=days)
        else:
            # 如果已过期或首次开通，从现在开始计算
            self.started_at = now
            self.expires_at = now + timezone.timedelta(days=days)
        self.is_active = True
        self.save()


class PaymentCallback(models.Model):
    """支付回调记录"""
    out_trade_no = models.CharField(max_length=64, verbose_name="商户订单号")
    trade_no = models.CharField(max_length=64, verbose_name="支付宝交易号")
    callback_data = models.JSONField(verbose_name="回调数据")
    processed = models.BooleanField(default=False, verbose_name="是否已处理")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "支付回调记录"
        verbose_name_plural = "支付回调记录"