from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analytics'

    def ready(self):
        # 注册信号处理
        from . import signals  # noqa: F401