from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import PosterTask


class PosterTaskAPITestCase(APITestCase):
    """海报任务API测试"""
    
    def test_create_poster_task(self):
        """测试创建海报任务"""
        data = {
            'title': '测试海报',
            'prompt': '生成一张科技感的海报'
        }
        response = self.client.post('/api/posters/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PosterTask.objects.count(), 1)
        self.assertEqual(PosterTask.objects.get().title, '测试海报')
    
    def test_list_poster_tasks(self):
        """测试获取海报任务列表"""
        PosterTask.objects.create(title='任务1', prompt='提示词1')
        PosterTask.objects.create(title='任务2', prompt='提示词2')
        
        response = self.client.get('/api/posters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_poster_task(self):
        """测试获取单个海报任务"""
        task = PosterTask.objects.create(title='测试任务', prompt='测试提示词')
        
        response = self.client.get(f'/api/posters/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '测试任务')
    
    def test_generate_poster(self):
        """测试触发海报生成"""
        task = PosterTask.objects.create(title='测试任务', prompt='测试提示词')
        
        response = self.client.post(f'/api/posters/{task.id}/generate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        task.refresh_from_db()
        self.assertEqual(task.status, 'processing')


class PosterTaskModelTestCase(TestCase):
    """海报任务模型测试"""
    
    def test_create_poster_task(self):
        """测试创建海报任务模型"""
        task = PosterTask.objects.create(
            title='测试海报',
            prompt='生成一张科技感的海报'
        )
        self.assertEqual(task.status, 'pending')
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)
    
    def test_poster_task_str(self):
        """测试海报任务字符串表示"""
        task = PosterTask.objects.create(
            title='测试海报',
            prompt='测试提示词'
        )
        self.assertEqual(str(task), '测试海报 - pending')

