from django.urls import path
from .views import *

urlpatterns = [
    # path('', SeriesListView.as_view(), name='series-list'),
    path("series/", SeriesListView.as_view(), name="series-list"),
    path("series/crawl/", SeriesView.as_view(), name="series-crawl"),
    path("series/<int:series_id>/", SeriesDetailView.as_view(), name="series-detail"),
    path(
        "series/<int:series_id>/episode/crawl",
        EpisodeCrawlView.as_view(),
        name="episode-crawl",
    ),
    path(
        "series/<int:series_id>/episode/",
        EpisodeListView.as_view(),
        name="episode-list",
    ),
    path(
        "episode/<int:product_id>/",
        EpisodeDetailView.as_view(),
        name="episode-detail",
    ),
    path(
        "episode/<int:product_id>/comment",
        CommentListView.as_view(),
        name="comment",
    ),
    path(
        "episode/<int:product_id>/comment/crawl",
        CommentCrawlView.as_view(),
        name="comment-crawl",
    ),
]
