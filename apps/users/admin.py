from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # 按你的用户模型实际字段配置
    search_fields = ('id','username')