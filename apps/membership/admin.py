from django.contrib import admin
from .models import MembershipPlan, MembershipOrder, UserMembership, PaymentCallback


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'original_price', 'duration_days', 'is_active', 'is_featured')
    list_filter = ('plan_type', 'is_active', 'is_featured')
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'price')
    list_editable = ('is_active', 'is_featured', 'price')


@admin.register(MembershipOrder)
class MembershipOrderAdmin(admin.ModelAdmin):
    list_display = ('out_trade_no', 'user', 'plan', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('out_trade_no', 'trade_no', 'user__username')
    readonly_fields = ('out_trade_no', 'trade_no', 'alipay_response')
    ordering = ('-created_at',)


@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_active', 'started_at', 'expires_at', 'total_orders', 'total_spent')
    list_filter = ('is_active', 'plan')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('total_orders', 'total_spent')


@admin.register(PaymentCallback)
class PaymentCallbackAdmin(admin.ModelAdmin):
    list_display = ('out_trade_no', 'trade_no', 'processed', 'created_at')
    list_filter = ('processed', 'created_at')
    search_fields = ('out_trade_no', 'trade_no')
    readonly_fields = ('callback_data',)