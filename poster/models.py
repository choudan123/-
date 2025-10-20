from django.db import models


class PosterTask(models.Model):
    """海报生成任务模型"""
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('processing', '生成中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    title = models.CharField('标题', max_length=200)
    prompt = models.TextField('生成提示词')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    image_url = models.URLField('图片URL', blank=True, null=True)
    image = models.ImageField('海报图片', upload_to='posters/', blank=True, null=True)
    error_message = models.TextField('错误信息', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '海报任务'
        verbose_name_plural = '海报任务'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.status}"

