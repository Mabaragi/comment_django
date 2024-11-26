from django.urls import path
from . import views
from . views import UserListView

urlpatterns = [
    path('', views.get_index, name='get_movies_data'),
    path('apiview', UserListView.as_view(), name='user-list'),
]