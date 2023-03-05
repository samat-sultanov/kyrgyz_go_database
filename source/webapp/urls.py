from django.urls import path

from .views import file_upload, IndexView, NewsListView, PlayerSearch, TournamentSearch, CalendarCreateView, \
    CalendarUpdateView, CalendarDeleteView, CompetitorSearch, ClubsListView, PlayerDetail, TournamentDetail

app_name = 'webapp'


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('player_search/', PlayerSearch.as_view(), name='player_search'),
    path('player_detail/<int:pk>', PlayerDetail.as_view(), name='player_detail'),
    path('file_upload/', file_upload, name='file_upload'),
    path('news/', NewsListView.as_view(), name='news_list'),
    path('clubs/', ClubsListView.as_view(), name='clubs_list'),
    path('event_create/', CalendarCreateView.as_view(), name='event_create'),
    path('event_update/<int:pk>/', CalendarUpdateView.as_view(), name='event_update'),
    path('event_delete/<int:pk>/', CalendarDeleteView.as_view(), name='event_delete'),
    path('tournament_search/', TournamentSearch.as_view(), name='tournament_search'),
    path('tournament_search/<int:pk>/', TournamentDetail.as_view(), name='tournament_detail'),
    path('competitors/', CompetitorSearch.as_view(), name='competitor_search'),
]
