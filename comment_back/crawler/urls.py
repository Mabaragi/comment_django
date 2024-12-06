from django.urls import path
from . views import SeriesListView, SeriesView

urlpatterns = [
    # path('', SeriesListView.as_view(), name='series-list'),
    path('', SeriesView.as_view(), name='series'),
]