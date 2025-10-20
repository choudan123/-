from django.db.models import F
from django.contrib.auth import get_user_model

User = get_user_model()

def consume_free_quota(user):
    """
    非会员且剩余免费次数 > 0 时安全扣减 1
    """
    if not user.is_authenticated:
        return
    if getattr(user, 'is_member', False):
        return
    if getattr(user, 'free_poster_count', 0) <= 0:
        return
    User.objects.filter(id=user.id, free_poster_count__gt=0).update(free_poster_count=F('free_poster_count') - 1)