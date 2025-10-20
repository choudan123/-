from rest_framework import serializers

class ComposePromptSerializer(serializers.Serializer):
    # 从数据库模型选择的字段
    scene_id = serializers.IntegerField(required=False, allow_null=True)
    poster_type_id = serializers.IntegerField(required=False, allow_null=True)
    style_id = serializers.IntegerField(required=False, allow_null=True)
    layout_id = serializers.IntegerField(required=False, allow_null=True)
    font_id = serializers.IntegerField(required=False, allow_null=True)
    size_id = serializers.IntegerField(required=False, allow_null=True)  # 用于生成 size 参数
    aspect_ratio_id = serializers.IntegerField(required=False, allow_null=True)
    reference_image_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)