from django.db import models
from django.conf import settings

class Poster(models.Model):
    """
    海报生成记录模型
    保存每一次海报生成的所有关键信息，包括用户、模板、AI生成结果等
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prompt = models.TextField()                             # 实际用于生成的提示词
    images = models.JSONField(default=list)                 # 生成的图片URL列表
    status = models.CharField(max_length=20, default='pending')  # 生成状态：pending/success/failed
    error_message = models.TextField(blank=True, null=True) # 异常信息（如有）
    created_at = models.DateTimeField(auto_now_add=True)    # 创建时间
    updated_at = models.DateTimeField(auto_now=True)        # 更新时间

    def __str__(self):
        return f"Poster#{self.id} - {self.user_id}"