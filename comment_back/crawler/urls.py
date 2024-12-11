from django.urls import path
from .views import *

urlpatterns = [
    # path('', SeriesListView.as_view(), name='series-list'),
    path("series/", SeriesView.as_view(), name="series"),
    path("series/<int:series_id>/episode/", EpisodeView.as_view(), name="episode"),
    path(
        "series/<int:series_id>/episode/<int:product_id>/comment",
        CommentView.as_view(),
        name="comment",
    ),
]
