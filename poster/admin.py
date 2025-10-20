from django.contrib import admin
from .models import PosterTask


@admin.register(PosterTask)
class PosterTaskAdmin(admin.ModelAdmin):
    """海报任务管理"""
    list_display = ['id', 'title', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'prompt']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'prompt', 'status')
        }),
        ('生成结果', {
            'fields': ('image_url', 'image', 'error_message')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )

