from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.poster_enums.models import (
    Scene, PosterType, Style, Layout, Size, AspectRatio, ReferenceImage, Font
)
from apps.poster_enums.prompt_serializers import ComposePromptSerializer


class PromptViewSet(viewsets.ViewSet):
    """
    提示词组合功能：将模型数据组合成带类型标识的提示词
    """

    @action(methods=["post"], detail=False, url_path="compose")
    def compose(self, request):
        """
        根据模型数据组合生成带类型标识的提示词
        """
        ser = ComposePromptSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        prompt_parts = []

        # 应用场景
        scene = Scene.objects.filter(id=data["scene_id"], is_active=True).first() if data.get("scene_id") else None
        if scene:
            prompt_parts.append(f"应用场景：{scene.name}")

        # 海报类型
        poster_type = PosterType.objects.filter(id=data["poster_type_id"], is_active=True).first() if data.get("poster_type_id") else None
        if poster_type:
            prompt_parts.append(f"海报类型：{poster_type.name}")

        # 风格
        style = Style.objects.filter(id=data["style_id"], is_active=True).first() if data.get("style_id") else None
        if style:
            prompt_parts.append(f"风格：{style.name}")

        # 布局
        layout = Layout.objects.filter(id=data["layout_id"], is_active=True).first() if data.get("layout_id") else None
        if layout:
            prompt_parts.append(f"布局：{layout.name}")

        # 字体
        font = Font.objects.filter(id=data["font_id"], is_active=True).first() if data.get("font_id") else None
        if font:
            prompt_parts.append(f"字体：{font.name}")

        # 宽高比（用于提示词描述）
        aspect_ratio = AspectRatio.objects.filter(id=data["aspect_ratio_id"], is_active=True).first() if data.get("aspect_ratio_id") else None
        if aspect_ratio:
            prompt_parts.append(f"画面比例：{aspect_ratio.name}")

        # 参考图片
        refs = []
        if data.get("reference_image_ids"):
            refs = list(ReferenceImage.objects.filter(id__in=data["reference_image_ids"], is_active=True))
            if refs:
                ref_names = [ref.name for ref in refs]
                prompt_parts.append(f"参考风格：{' '.join(ref_names)}")

        # 拼接提示词
        prompt = "；".join(prompt_parts) if prompt_parts else ""

        # 获取 size（用于传给 Ark API）
        size = Size.objects.filter(id=data["size_id"], is_active=True).first() if data.get("size_id") else None
        ark_size = size.name if size else "2K"  # 默认 2K

        return Response({
            "prompt": prompt,
            "size": ark_size,  # 单独返回给 Ark API 使用
            "meta": {
                "scene": {"id": scene.id, "name": scene.name} if scene else None,
                "poster_type": {"id": poster_type.id, "name": poster_type.name} if poster_type else None,
                "style": {"id": style.id, "name": style.name} if style else None,
                "layout": {"id": layout.id, "name": layout.name} if layout else None,
                "font": {"id": font.id, "name": font.name} if font else None,
                "size": {"id": size.id, "name": size.name} if size else None,
                "aspect_ratio": {"id": aspect_ratio.id, "name": aspect_ratio.name} if aspect_ratio else None,
                "reference_images": [{"id": ref.id, "name": ref.name} for ref in refs]
            }
        })