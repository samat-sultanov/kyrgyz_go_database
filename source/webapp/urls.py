from django.urls import path
from .views import file_upload, Player_Detail, IndexView, NewsListView, Player_Search, TournamentSearch, CalendarCreateView , CalendarUpdateView , CalendarDeleteView

app_name = 'webapp'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('player_search/', Player_Search.as_view(), name='player_search'),
    path('player_detail/<int:pk>', Player_Detail.as_view(), name='player_detail'),
    path('file_upload/', file_upload, name='file_upload'),
    path('news/', NewsListView.as_view(), name='news_list'),
    path('event_create/', CalendarCreateView.as_view(), name='event_create'),
    path('event_update/<int:pk>/', CalendarUpdateView.as_view(), name='event_update'),
    path('event_delete/<int:pk>/', CalendarDeleteView.as_view(), name='event_delete'),
    path('tournament_search/', TournamentSearch.as_view(), name='tournament_search'),
]
