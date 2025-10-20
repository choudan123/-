from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PosterTaskViewSet

router = DefaultRouter()
router.register(r'posters', PosterTaskViewSet, basename='poster')

urlpatterns = [
    path('', include(router.urls)),
]
