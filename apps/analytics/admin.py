from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import PosterEvent, SceneTypeStyleStat

User = get_user_model()


def _user_lookup_fields():
    """
    动态生成 user 关联的搜索字段：
    - 优先使用自定义用户模型的 USERNAME_FIELD
    - 退而求其次尝试常见字段：username、email、mobile、phone、nickname、nick_name、name
    仅返回用户模型里真实存在的字段，避免“无法解析 admin 字段”的错误
    """
    candidates = [
        getattr(User, 'USERNAME_FIELD', None),  # 自定义登录字段
        'username', 'email', 'mobile', 'phone', 'nickname', 'nick_name', 'name',
    ]
    # 去除 None 和重复
    candidates = [c for c in candidates if c]
    # 收集用户模型上真实存在的字段名
    user_field_names = {f.name for f in User._meta.get_fields() if getattr(f, 'concrete', False) or hasattr(f, 'attname')}
    # 仅生成存在的搜索路径
    return [f'user__{fld}' for fld in candidates if fld in user_field_names]


@admin.register(PosterEvent)
class PosterEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'scene', 'poster_type', 'style', 'event', 'created_at')
    list_filter = ('event', 'scene', 'poster_type', 'style', 'created_at')
    # 提示：autocomplete_fields 对 user 生效，要求“用户模型在其 Admin 中也配置了 search_fields”
    autocomplete_fields = ('user', 'scene', 'poster_type', 'style')
    list_select_related = ('user', 'scene', 'poster_type', 'style')
    date_hierarchy = 'created_at'

    def get_search_fields(self, request):
        # 动态组合用户搜索字段 + 其它外键的名称搜索
        base = ['scene__name', 'poster_type__name', 'style__name', 'event']
        return tuple(_user_lookup_fields() + base)


@admin.register(SceneTypeStyleStat)
class SceneTypeStyleStatAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'scene', 'poster_type', 'style', 'decayed_score', 'last_updated_at',
        'view_count', 'select_type_count', 'select_style_count', 'generate_count', 'download_count'
    )
    list_filter = ('scene', 'poster_type', 'style')
    search_fields = ('scene__name', 'poster_type__name', 'style__name')
    list_select_related = ('scene', 'poster_type', 'style')