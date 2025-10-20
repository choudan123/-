from django.db import models
from django.conf import settings
from django.utils import timezone
import math

from apps.poster_enums.models import Scene, PosterType, Style
from .constants import EVENT_CHOICES, EVENT_WEIGHTS, LAMBDA

User = settings.AUTH_USER_MODEL


class PosterEvent(models.Model):
    """
    用户在 场景×类型×风格 上的一次行为事件
    """
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    scene = models.ForeignKey(Scene, null=True, blank=True, on_delete=models.SET_NULL)
    poster_type = models.ForeignKey(PosterType, null=True, blank=True, on_delete=models.SET_NULL)
    style = models.ForeignKey(Style, null=True, blank=True, on_delete=models.SET_NULL)

    event = models.CharField(max_length=32, choices=EVENT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['scene']),
            models.Index(fields=['poster_type']),
            models.Index(fields=['style']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.event} s={self.scene_id} t={self.poster_type_id} st={self.style_id}'


class SceneTypeStyleStat(models.Model):
    """
    三元组统计（场景×类型×风格）
    使用指数时间衰减的累计得分：
      score(now) = score(prev) * exp(-λ * Δt) + weight(event)
    """
    scene = models.ForeignKey(Scene, on_delete=models.CASCADE)
    poster_type = models.ForeignKey(PosterType, on_delete=models.CASCADE)
    style = models.ForeignKey(Style, on_delete=models.CASCADE)

    decayed_score = models.FloatField(default=0.0)
    last_updated_at = models.DateTimeField(default=timezone.now)

    # 原始计数（便于审计/看板）
    view_count = models.PositiveIntegerField(default=0)
    select_type_count = models.PositiveIntegerField(default=0)
    select_style_count = models.PositiveIntegerField(default=0)
    generate_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('scene', 'poster_type', 'style')
        indexes = [
            models.Index(fields=['scene', 'poster_type']),
            models.Index(fields=['scene', 'style']),
            models.Index(fields=['poster_type', 'style']),
            models.Index(fields=['scene']),
        ]

    def apply_event(self, event_code, now=None):
        # 先按时间衰减，再叠加事件权重
        now = now or timezone.now()
        delta_days = (now - self.last_updated_at).total_seconds() / 86400.0
        # 避免负值
        if delta_days < 0:
            delta_days = 0.0
        decay = math.exp(-LAMBDA * delta_days)
        self.decayed_score *= decay

        self.decayed_score += EVENT_WEIGHTS.get(event_code, 0.0)

        if event_code == 'VIEW':
            self.view_count += 1
        elif event_code == 'SELECT_TYPE':
            self.select_type_count += 1
        elif event_code == 'SELECT_STYLE':
            self.select_style_count += 1
        elif event_code == 'GENERATE':
            self.generate_count += 1
        elif event_code == 'DOWNLOAD':
            self.download_count += 1

        self.last_updated_at = now