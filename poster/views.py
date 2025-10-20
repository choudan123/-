from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PosterTask
from .serializers import PosterTaskSerializer, PosterTaskCreateSerializer


class PosterTaskViewSet(viewsets.ModelViewSet):
    """海报任务视图集"""
    queryset = PosterTask.objects.all()
    serializer_class = PosterTaskSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PosterTaskCreateSerializer
        return PosterTaskSerializer
    
    def create(self, request, *args, **kwargs):
        """创建海报生成任务"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # 返回完整的任务信息
        task = PosterTask.objects.get(pk=serializer.instance.pk)
        response_serializer = PosterTaskSerializer(task)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """触发海报生成"""
        task = self.get_object()
        
        if task.status == 'completed':
            return Response(
                {'message': '任务已完成'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 这里可以集成 Doubao-Seedream-4.0 API
        # 暂时只更新状态
        task.status = 'processing'
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)

