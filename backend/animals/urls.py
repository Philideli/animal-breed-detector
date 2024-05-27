from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import run_analysis, rerun_analysis, analysis_detail, analyses_overview, image_original, image_result

urlpatterns = [
    path('analysis/run', run_analysis, name='analysis-run'),
    path('analysis/<int:id>/rerun', rerun_analysis, name='analysis-rerun'),
    path('analysis/<int:id>/image/original', image_original, name='analysis-image-original'),
    path('analysis/<int:id>/image/result', image_result, name='analysis-image-result'),
    path('analysis/<int:id>', analysis_detail, name='analysis-detail'),
    path('analyses/overview', analyses_overview, name='analyses-overview'),
]

urlpatterns = format_suffix_patterns(urlpatterns)