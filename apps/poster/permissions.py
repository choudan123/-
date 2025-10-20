from rest_framework.permissions import BasePermission

class IsMemberOrHasFreeTimes(BasePermission):
    """
    会员无限制，普通用户有免费海报生成次数限制
    """
    message = "普通用户免费海报生成次数已用尽，请升级为会员。"

    def has_permission(self, request, view):
        user = request.user
        if hasattr(user, 'is_member') and user.is_member:
            return True
        # 非会员，检查剩余免费次数
        return getattr(user, 'free_poster_count', 0) > 0