from django.urls import path
from .views import LogEventView, RecommendTypesView, RecommendStylesView

urlpatterns = [
    path('event/', LogEventView.as_view(), name='log_event'),
    path('recommend/types/', RecommendTypesView.as_view(), name='recommend_types'),
    path('recommend/styles/', RecommendStylesView.as_view(), name='recommend_styles'),
]