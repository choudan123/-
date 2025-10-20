from django.urls import path
from .views import (
    PosterGenerateView,
    PosterConfigView,
    PosterHistoryView,
    PosterUsageView,
)
from .views_upload import PosterImageUploadView

urlpatterns = [
    path('generate/', PosterGenerateView.as_view(), name='poster-generate'),
    path('config/', PosterConfigView.as_view(), name='poster-config'),
    path('history/', PosterHistoryView.as_view(), name='poster-history'),
    path('usage/', PosterUsageView.as_view(), name='poster-usage'),
    path('upload-image/', PosterImageUploadView.as_view(), name='poster-upload-image'),
]