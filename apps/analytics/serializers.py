from rest_framework import serializers
from .constants import EVENT_CHOICES

class LogEventSerializer(serializers.Serializer):
    scene_id = serializers.IntegerField(required=False, allow_null=True)
    poster_type_id = serializers.IntegerField(required=False, allow_null=True)
    style_id = serializers.IntegerField(required=False, allow_null=True)
    event = serializers.ChoiceField(choices=[c[0] for c in EVENT_CHOICES])

class RecommendTypesQuery(serializers.Serializer):
    scene_id = serializers.IntegerField()
    top_n = serializers.IntegerField(required=False, default=6)

class RecommendStylesQuery(serializers.Serializer):
    scene_id = serializers.IntegerField()
    poster_type_id = serializers.IntegerField()
    top_n = serializers.IntegerField(required=False, default=6)