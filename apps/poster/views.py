from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
import re

from .models import Poster
from .serializers import PosterCreateSerializer, PosterSerializer
from .services import generate_poster
from apps.poster_enums.models import Size, AspectRatio
from .permissions import IsMemberOrHasFreeTimes
from .utils import consume_free_quota


def _ark_size_from_size(size: Size) -> str:
    """
    从 Size.name 解析 Ark 尺寸：
    - 1K/2K/4K/8K -> 原样
    """
    name = (size.name or "").strip()
    if not name:
        return "2048x2048"
    up = name.upper()
    if up in {"2K", "4K"}:
        return up
    m = re.search(r"(\d{3,5})\s*[x×]\s*(\d{3,5})", name, re.I)
    if m:
        return f"{m.group(1)}x{m.group(2)}"
    return "2048x2048"


def _ensure_prompt_has_count(n: int, prompt: str) -> str:
    """
    若提示词中没有“数量”语义，则在最前面加上“生成N张图片：”
    仅在组图且传入 image_count_hint 时使用。
    """
    # 容错：n 非法时直接返回原提示
    if not isinstance(n, int) or n < 1:
        return (prompt or "").strip()

    p = (prompt or "").strip()

    # 已含数量语义则不再重复（中英常见写法）
    patterns = [
        r"\b(?:generate|create)\s*(\d{1,2})\s*(?:images?|pictures?|photos?)\b",
        r"生成\s*(\d{1,2})\s*张(?:图片)?",
        r"(\d{1,2})\s*张(?:图片)?",
    ]
    for pat in patterns:
        if re.search(pat, p, flags=re.IGNORECASE):
            return p

    # 前置数量语义
    lead = f"生成{n}张图片"
    if not p:
        return f"{lead}。"
    # 用中文标点更顺滑
    return f"{lead}：{p}"

class PosterGenerateView(APIView):
    """
    统一海报生成接口
    - 单图: generation_mode=single -> sequential_image_generation=disabled
    - 组图: generation_mode=group  -> sequential_image_generation=auto
      数量由提示词决定；sequential_image_generation_options.max_images 仅为上限
    """
    permission_classes = [IsAuthenticated, IsMemberOrHasFreeTimes]

    def post(self, request):
        serializer = PosterCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        size = Size.objects.filter(id=data["size_id"], is_active=True).first()
        if not size:
            return Response({"detail": "尺寸不存在或未启用"}, status=status.HTTP_400_BAD_REQUEST)

        ark_size = _ark_size_from_size(size)

        # 参考图：优先 images，否则 image_url
        ref_images = data.get("images") or []
        image_single = data.get("image_url") if not ref_images else None

        # 提示词：若是组图且给了 image_count_hint，但提示词里没数量语义，则补一句“生成N张图片”
        prompt = (data.get("prompt") or "").strip()
        if data.get("generation_mode") == "group" and data.get("image_count_hint"):
            prompt = _ensure_prompt_has_count(int(data["image_count_hint"]), prompt)

        result = generate_poster(
            prompt=prompt,
            size=ark_size,
            image=image_single,
            images=ref_images if ref_images else None,
            sequential_image_generation=data.get("sequential_image_generation", "disabled"),
            sequential_image_generation_options=data.get("sequential_image_generation_options"),
            response_format="url",
            watermark=False,
            stream=data.get("stream", False),
        )

        with transaction.atomic():
            poster = Poster.objects.create(
                user=request.user,
                prompt=prompt,
                images=result.get("urls", []),
                status="success" if result.get("success") else "failed",
                error_message=result.get("error"),
            )
            if result.get("success") and not getattr(request.user, "is_member", False):
                consume_free_quota(request.user)

        return Response(
            PosterSerializer(poster).data,
            status=status.HTTP_201_CREATED if result.get("success") else status.HTTP_400_BAD_REQUEST,
        )


class PosterConfigView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        sizes = Size.objects.filter(is_active=True).values("id", "name")
        aspect_ratios = AspectRatio.objects.filter(is_active=True).values("id", "name", "ratio_w", "ratio_h")
        return Response({"sizes": list(sizes), "aspect_ratios": list(aspect_ratios)})


class PosterHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posters = Poster.objects.filter(user=request.user).order_by("-created_at")[:200]
        return Response(PosterSerializer(posters, many=True).data)


class PosterUsageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "is_member": getattr(request.user, "is_member", False),
                "free_remaining": getattr(request.user, "free_poster_count", 0),
            }
        )