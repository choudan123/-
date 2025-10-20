from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import CustomUser

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # 指定API需要接收的字段
        fields = ['username', 'password', 'nickname', 'email']
        # 对特殊字段进行额外设置
        extra_kwargs = {
            'password': {
                'write_only': True,  # 密码是只写的，API查询用户时不应返回密码
                'style': {'input_type': 'password'}, # 在DRF的API浏览界面，显示为密码输入框
                'min_length': 8, # 密码最小长度
                'error_messages': {
                    'min_length': '密码长度至少为8位。'
                }
            }
        }

    def create(self, validated_data):
        """
        重写 create 方法，用于在创建用户时对密码进行加密。
        """
        # 使用 Django 内置的 make_password 函数对密码进行加密
        validated_data['password'] = make_password(validated_data.get('password'))
        # 调用父类的 create 方法创建用户
        user = super().create(validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户个人信息序列化器
    """
    is_member = serializers.ReadOnlyField()  # 添加会员状态
    avatar_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    class Meta:
        model = CustomUser
        fields = ['username', 'nickname', 'email','avatar_url','is_member']
        read_only_fields = ['username']