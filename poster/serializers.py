from rest_framework import serializers
from .models import PosterTask


class PosterTaskSerializer(serializers.ModelSerializer):
    """海报任务序列化器"""
    
    class Meta:
        model = PosterTask
        fields = [
            'id', 'title', 'prompt', 'status', 
            'image_url', 'image', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'image_url', 'image', 'error_message', 'created_at', 'updated_at']


class PosterTaskCreateSerializer(serializers.ModelSerializer):
    """海报任务创建序列化器"""
    
    class Meta:
        model = PosterTask
        fields = ['title', 'prompt']
