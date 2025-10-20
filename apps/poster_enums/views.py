from rest_framework import viewsets
from .models import (
    Scene, PosterType, Style, ColorScheme, Layout, Size, AspectRatio,
    Font, ReferenceImage
)
from .serializers import (
    SceneSerializer, PosterTypeSerializer, StyleSerializer,
    ColorSchemeSerializer, LayoutSerializer, SizeSerializer, AspectRatioSerializer,
    FontSerializer, ReferenceImageSerializer
)

class SceneViewSet(viewsets.ModelViewSet):
    queryset = Scene.objects.filter(is_active=True)
    serializer_class = SceneSerializer

class PosterTypeViewSet(viewsets.ModelViewSet):
    queryset = PosterType.objects.filter(is_active=True)
    serializer_class = PosterTypeSerializer

class StyleViewSet(viewsets.ModelViewSet):
    queryset = Style.objects.filter(is_active=True)
    serializer_class = StyleSerializer

class ColorSchemeViewSet(viewsets.ModelViewSet):
    queryset = ColorScheme.objects.filter(is_active=True)
    serializer_class = ColorSchemeSerializer

class LayoutViewSet(viewsets.ModelViewSet):
    queryset = Layout.objects.filter(is_active=True)
    serializer_class = LayoutSerializer

class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.filter(is_active=True)
    serializer_class = SizeSerializer

class AspectRatioViewSet(viewsets.ModelViewSet):
    queryset = AspectRatio.objects.filter(is_active=True)
    serializer_class = AspectRatioSerializer

class FontViewSet(viewsets.ModelViewSet):
    queryset = Font.objects.filter(is_active=True)
    serializer_class = FontSerializer

class ReferenceImageViewSet(viewsets.ModelViewSet):
    queryset = ReferenceImage.objects.filter(is_active=True)
    serializer_class = ReferenceImageSerializer