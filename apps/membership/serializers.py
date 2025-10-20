from rest_framework import serializers
from .models import MembershipPlan, MembershipOrder, UserMembership


class MembershipPlanSerializer(serializers.ModelSerializer):
    """会员套餐序列化器"""
    discount_percentage = serializers.ReadOnlyField()

    class Meta:
        model = MembershipPlan
        fields = [
            'id', 'name', 'plan_type', 'price', 'original_price',
            'duration_days', 'description', 'features', 'poster_quota',
            'max_image_size', 'priority_generation', 'is_featured',
            'discount_percentage'
        ]


class CreateMembershipPlanSerializer(serializers.ModelSerializer):
    """创建会员套餐序列化器"""

    class Meta:
        model = MembershipPlan
        fields = [
            'name', 'plan_type', 'price', 'original_price',
            'duration_days', 'description', 'features', 'poster_quota',
            'max_image_size', 'priority_generation', 'is_featured',
            'sort_order'
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("价格必须大于0")
        return value

    def validate_duration_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("有效期天数必须大于0")
        return value


class CreateMembershipOrderSerializer(serializers.Serializer):
    """创建会员订单序列化器"""
    plan_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=MembershipOrder.PAYMENT_METHODS)

    def validate_plan_id(self, value):
        try:
            plan = MembershipPlan.objects.get(id=value, is_active=True)
        except MembershipPlan.DoesNotExist:
            raise serializers.ValidationError("套餐不存在或已下架")
        return value


class MembershipOrderSerializer(serializers.ModelSerializer):
    """会员订单序列化器"""
    plan = MembershipPlanSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = MembershipOrder
        fields = [
            'out_trade_no', 'user', 'plan', 'amount', 'status',
            'payment_method', 'trade_no', 'expires_at', 'paid_at',
            'created_at'
        ]


class UserMembershipSerializer(serializers.ModelSerializer):
    """用户会员信息序列化器"""
    plan = MembershipPlanSerializer(read_only=True)
    is_expired = serializers.ReadOnlyField()
    days_left = serializers.SerializerMethodField()

    class Meta:
        model = UserMembership
        fields = [
            'plan', 'is_active', 'started_at', 'expires_at',
            'is_expired', 'days_left', 'total_orders', 'total_spent'
        ]

    def get_days_left(self, obj):
        """剩余天数"""
        if not obj.expires_at or obj.is_expired:
            return 0
        from django.utils import timezone
        delta = obj.expires_at - timezone.now()
        return max(0, delta.days)