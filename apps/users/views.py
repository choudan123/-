from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegisterSerializer, UserProfileSerializer
from django.conf import settings
from django.core.files.storage import default_storage
import os, uuid

#注册视图
class UserRegisterView(APIView):
    permission_classes = [AllowAny]  # 允许所有用户访问

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "注册成功！"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#登录视图

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 添加额外的返回字段
        token['username'] = user.username
        token['nickname'] = user.nickname
        token['is_member'] = user.is_member  # 添加会员状态
        return token

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(APIView):
    """
    获取和更新用户个人信息
    """
    permission_classes = [IsAuthenticated]  # 需要登录才能访问

    def get(self, request):
        """
        获取当前登录用户的个人信息
        """
        user = request.user  # 获取当前登录的用户实例
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        """
        修改用户的 nickname 和 email
        """
        user = request.user  # 当前登录的用户
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error": "旧密码不正确"}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password or len(new_password) < 8:
            return Response({"error": "新密码长度至少为8位"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        # 要求前端重新登录（注销本地 token）
        return Response({"message": "密码修改成功"}, status=status.HTTP_200_OK)

class AvatarUploadView(APIView):
    """
    接收 multipart/form-data 的 file 字段，保存图片并更新用户 avatar_url
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '未收到文件'}, status=400)

        # 简单类型校验
        allowed = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
        if file.content_type not in allowed:
            return Response({'error': '仅支持 JPG/PNG/WEBP/GIF'}, status=400)

        # 生成保存路径：media/avatars/<user_id>/<uuid>.<ext>
        _, ext = os.path.splitext(file.name)
        ext = (ext or '.jpg').lower()
        path = f'avatars/{request.user.id}/{uuid.uuid4().hex}{ext}'
        saved_path = default_storage.save(path, file)  # 相对 MEDIA_ROOT 的路径

        # 生成可访问 URL（开发环境用 MEDIA_URL 静态服务）
        url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, saved_path).replace('\\', '/'))

        # 写回用户
        u = request.user
        u.avatar_url = url
        u.save(update_fields=['avatar_url'])

        return Response({'avatar_url': url}, status=200)