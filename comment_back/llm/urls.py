from django.urls import path
from .views import *


urlpatterns = [
    path(
        "api/emotion-analysis/<int:episode_id>/",
        CommentEmotionAnalysisView.as_view(),
        name="emotion-analysis",
    ),
    path(
        "api/emotion-analysis/<int:comment_id>/delete/",
        CommentAnalysisResultDestroyView.as_view(),
        name="emotion-analysis-delete",
    ),
    path(
        "api/summary-analysis/<int:episode_id>/",
        CommentsSummaryResultView.as_view(),
        name="summary",
    ),
]
