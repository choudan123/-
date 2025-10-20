from django.urls import path
from .views import UserRegisterView,LoginView,UserProfileView, ChangePasswordView,AvatarUploadView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'), #注册接口
    path('login/', LoginView.as_view(), name='login'),          # 登录接口
    path('profile/', UserProfileView.as_view(), name='user-profile'),  # 用户个人信息接口
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),  # 修改密码接口
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 刷新 access
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # 校验 token
    path('avatar/upload/', AvatarUploadView.as_view(), name='avatar-upload'),
]