from rest_framework import serializers
from .models import Poster


class PosterCreateSerializer(serializers.Serializer):
    """
    统一的海报生成请求（组图数量由提示词决定；max_images 仅作为上限）
    - 必填: size_id, aspect_ratio_id
    - 可选: prompt 以及若干上下文字段（保留以便后续 prompt 组装）
    - 参考图: image_url(单个) 或 images(多个) 二选一；两者都不给也可以（文生）
    - 模式:
        single -> sequential_image_generation = "disabled"（输出 1 张）
        group  -> sequential_image_generation = "auto"，输出张数由提示词决定，
                  sequential_image_generation_options.max_images 仅限制“最多输出几张（上限）”
    - 兼容历史字段:
        max_images 与 sequential_image_generation（若提供将被规范化）
    - 新增:
        image_count_hint: 可选 1~15，若提供且为 group，会用于“往 prompt 里补一句生成 N 张图片”的语义提示
    """

    # 基础
    prompt = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    size_id = serializers.IntegerField(required=True)
    aspect_ratio_id = serializers.IntegerField(required=True)

    # 可选上下文（保留/未使用也不报错）
    scene_id = serializers.IntegerField(required=False)
    poster_type_id = serializers.IntegerField(required=False)
    style_id = serializers.IntegerField(required=False)
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    keywords = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    negative_keywords = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    main_color = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    palette = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    layout_id = serializers.IntegerField(required=False)
    reference_image_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)
    font_id = serializers.IntegerField(required=False)

    # 默认提示控制
    include_quality_hints = serializers.BooleanField(required=False, default=True)
    include_default_negative = serializers.BooleanField(required=False, default=True)

    # 参考图（互斥）
    image_url = serializers.URLField(required=False)
    images = serializers.ListField(child=serializers.URLField(), required=False)

    # 模式与选项
    generation_mode = serializers.ChoiceField(choices=("single", "group"), required=False)
    sequential_image_generation = serializers.ChoiceField(choices=("disabled", "auto"), required=False)
    sequential_image_generation_options = serializers.DictField(required=False)

    # 兼容历史 max_images（现在只当“上限”来用，非必填）
    max_images = serializers.IntegerField(required=False, min_value=1, max_value=15)

    # 新增：组图张数提示（写进 prompt 的语义，不作为硬性数量）
    image_count_hint = serializers.IntegerField(required=False, min_value=1, max_value=15)

    def validate(self, attrs):
        # 参考图互斥
        if attrs.get("image_url") and attrs.get("images"):
            raise serializers.ValidationError("image_url 与 images 不能同时提供，请二选一")

        ref_count = 1 if attrs.get("image_url") else len(attrs.get("images") or [])
        if ref_count > 10:
            raise serializers.ValidationError("参考图片最多 10 张")

        # 推断模式
        mode = attrs.get("generation_mode")
        seq = attrs.get("sequential_image_generation")
        seq_opts = attrs.get("sequential_image_generation_options") or {}
        max_images_req = seq_opts.get("max_images")
        if max_images_req is None:
            max_images_req = attrs.get("max_images")  # 兼容历史字段

        if not mode:
            if seq == "auto" or (max_images_req and max_images_req > 1):
                mode = "group"
            else:
                mode = "single"
        attrs["generation_mode"] = mode

        # 规范化
        if mode == "single":
            # 单图：固定 1 张；参考图 0~10；禁用组图
            attrs["sequential_image_generation"] = "disabled"
            attrs.pop("sequential_image_generation_options", None)
            attrs.pop("max_images", None)
        else:
            # 组图：数量由提示词决定；max_images 仅作为上限（cap），非必填
            # 计算上限：若未传，则为 15 - 参考图数量；若传则取 min(传入, 15 - ref_count, 15)
            available = max(0, 15 - ref_count)
            if available <= 0:
                raise serializers.ValidationError("参考图数量过多，无法再生成新图（总数上限 15 张）")

            cap = max_images_req if max_images_req is not None else available
            cap = int(cap)
            cap = max(1, min(cap, available, 15))  # 至少 1，且不超过上限与总规则

            attrs["sequential_image_generation"] = "auto"
            attrs["sequential_image_generation_options"] = {"max_images": cap}
            attrs["max_images"] = cap  # 仅为兼容后续代码读取，不代表实际输出张数

            # image_count_hint 若提供，仅用作语义提示（由视图负责把语义补进 prompt）
            if "image_count_hint" in attrs:
                # 已由字段校验保证 1~15，这里不再处理
                pass

        return attrs


class PosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poster
        fields = "__all__"