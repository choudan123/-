from rest_framework import serializers
from .models import (
    Scene, PosterType, Style, ColorScheme, Layout, Size, AspectRatio,
    Font, ReferenceImage
)

class SceneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scene
        fields = '__all__'

class PosterTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PosterType
        fields = '__all__'

class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Style
        fields = '__all__'

class ColorSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorScheme
        fields = '__all__'

class LayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layout
        fields = '__all__'

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'

class AspectRatioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AspectRatio
        fields = '__all__'

class FontSerializer(serializers.ModelSerializer):
    class Meta:
        model = Font
        fields = '__all__'

class ReferenceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceImage
        fields = '__all__'