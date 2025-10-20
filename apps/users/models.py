from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

# 这就是我们一直在引用的 CustomUser 类
# 它继承了 Django 自带的 AbstractUser，并添加了我们自己的字段
class CustomUser(AbstractUser):
    """
    自定义用户模型
    """
    # 我们可以在这里添加自定义字段
    # 例如：昵称
    nickname = models.CharField(max_length=100, blank=True, null=True, verbose_name="昵称")

    # 例如：头像链接
    avatar_url = models.URLField(max_length=255, blank=True, null=True, verbose_name="头像链接")

    # 会员到期日
    membership_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="会员到期时间")

    #免费海报生成次数
    free_poster_count = models.IntegerField(default=10, verbose_name="免费海报生成次数")

    @property
    def is_member(self) -> bool:
        """
        是否为会员（返回布尔值）
        """
        return bool(self.membership_expires_at and self.membership_expires_at > now())

    def __str__(self):
        return self.username
