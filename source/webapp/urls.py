from django.urls import path
from .views import file_upload, IndexView, NewsListView, PlayerSearch, TournamentSearch

app_name = 'webapp'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('player_search/', PlayerSearch.as_view(), name='player_search'),
    path('file_upload/', file_upload, name='file_upload'),
    path('news/', NewsListView.as_view(), name='news_list'),
    path('tournament_search/', TournamentSearch.as_view(), name='tournament_search'),
]
