from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SceneViewSet, PosterTypeViewSet, StyleViewSet,
    ColorSchemeViewSet, LayoutViewSet, SizeViewSet, AspectRatioViewSet,
    FontViewSet, ReferenceImageViewSet
)
from .views_prompt import PromptViewSet

router = DefaultRouter()
router.register(r'scenes', SceneViewSet)
router.register(r'types', PosterTypeViewSet)
router.register(r'styles', StyleViewSet)
router.register(r'colors', ColorSchemeViewSet)
router.register(r'layouts', LayoutViewSet)
router.register(r'sizes', SizeViewSet)
router.register(r'aspect-ratios', AspectRatioViewSet)  # 替换 resolutions
router.register(r'fonts', FontViewSet)
router.register(r'reference-images', ReferenceImageViewSet)
router.register(r'prompt', PromptViewSet, basename='prompt')

urlpatterns = [
    path('', include(router.urls)),
]