from django.urls import path
from .views import file_upload, IndexView, NewsListView, Player_Search, ClubsListView

app_name = 'webapp'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('player_search/', Player_Search.as_view(), name='player_search'),
    path('file_upload/', file_upload, name='file_upload'),
    path('news/', NewsListView.as_view(), name='news_list'),
    path('clubs/', ClubsListView.as_view(), name='clubs_list'),
]