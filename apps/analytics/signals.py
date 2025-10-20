from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import PosterEvent, SceneTypeStyleStat

@receiver(post_save, sender=PosterEvent)
def on_poster_event_saved(sender, instance: PosterEvent, created: bool, **kwargs):
    # 仅在新事件创建时更新统计
    if not created:
        return
    # 三者缺一则不计（可按需放宽）
    if not (instance.scene_id and instance.poster_type_id and instance.style_id):
        return

    stat, _ = SceneTypeStyleStat.objects.get_or_create(
        scene_id=instance.scene_id,
        poster_type_id=instance.poster_type_id,
        style_id=instance.style_id,
    )
    stat.apply_event(instance.event, now=instance.created_at or timezone.now())
    stat.save()