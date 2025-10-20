from django.urls import path
from .views import (
    MembershipPlanListView,
    CreateMembershipPlanView,
    CreateMembershipOrderView,
    MembershipOrderListView,
    MembershipOrderDetailView,
    UserMembershipInfoView,
    AlipayNotifyView,
    PaymentResultView,
)

urlpatterns = [
    # 套餐管理
    path('plans/', MembershipPlanListView.as_view(), name='membership-plans'),
    path('plans/create/', CreateMembershipPlanView.as_view(), name='create-membership-plan'),

    # 订单管理
    path('orders/create/', CreateMembershipOrderView.as_view(), name='create-membership-order'),
    path('orders/', MembershipOrderListView.as_view(), name='membership-orders'),
    path('orders/<str:out_trade_no>/', MembershipOrderDetailView.as_view(), name='membership-order-detail'),

    # 会员信息
    path('info/', UserMembershipInfoView.as_view(), name='user-membership-info'),

    # 支付相关
    path('alipay/notify/', AlipayNotifyView.as_view(), name='alipay-notify'),
    path('payment-result/', PaymentResultView.as_view(), name='payment-result'),
]