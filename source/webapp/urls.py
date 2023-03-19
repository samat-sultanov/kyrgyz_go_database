from django.urls import path

from .views import file_upload, IndexView, NewsListView, PlayerSearch, TournamentSearch, CalendarCreateView, \
    CalendarUpdateView, CalendarDeleteView, CompetitorSearch, ClubsListView, PlayerDetail, TournamentDetail, \
    NewsCreateView, NewsDetailView, NewsUpdateView, NewsDeleteView, DeletedNewsListView, restore_one_deleted_news, \
    hard_delete_one_news, UpdatePlayer, about_us_view, DeletePlayer, file_upload_check, QuestionsListView, \
    ClubUpdate, ParticipantCreate, CalendarDetailView, ClubView, DeletedCalendarListView, restore_one_deleted_event, \
    hard_delete_one_event, RecommendationCreateView, send_feedback_to_admin, RecommendationUpdateView, \
    RecommendationDeleteView

app_name = 'webapp'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('player_search/', PlayerSearch.as_view(), name='player_search'),
    path('player_detail/<int:pk>', PlayerDetail.as_view(), name='player_detail'),
    path('update_player/<int:pk>', UpdatePlayer.as_view(), name='update_player'),
    path('delete_player/<int:pk>', DeletePlayer.as_view(), name='delete_player'),
    path('file_upload/', file_upload, name='file_upload'),
    path('news/', NewsListView.as_view(), name='news_list'),
    path('news/deleted_list/', DeletedNewsListView.as_view(), name='deleted_news_list'),
    path('news/restore/<int:pk>/', restore_one_deleted_news, name='news_restore_one_deleted'),
    path('news/hard_delete/<int:pk>/', hard_delete_one_news, name='news_hard_delete_one'),
    path('news_create/', NewsCreateView.as_view(), name='news_create'),
    path('news_detail/<int:pk>/', NewsDetailView.as_view(), name='news_detail'),
    path('news_update/<int:pk>/', NewsUpdateView.as_view(), name='news_update'),
    path('news_delete/<int:pk>/', NewsDeleteView.as_view(), name='news_delete'),
    path('clubs/', ClubsListView.as_view(), name='clubs_list'),
    path('clubs/<int:pk>/', ClubView.as_view(), name='club_view'),
    path('club_update/<int:pk>/', ClubUpdate.as_view(), name='club_update'),
    path('event_create/', CalendarCreateView.as_view(), name='event_create'),
    path('event_update/<int:pk>/', CalendarUpdateView.as_view(), name='event_update'),
    path('event_delete/<int:pk>/', CalendarDeleteView.as_view(), name='event_delete'),
    path('event_view/<int:pk>/', CalendarDetailView.as_view(), name='event_view'),
    path('event_restore/<int:pk>/', restore_one_deleted_event, name='event_restore_one_deleted'),
    path('event_hard_delete/<int:pk>/', hard_delete_one_event, name='event_hard_delete_one'),
    path('deleted_events_list/', DeletedCalendarListView.as_view(), name='deleted_calendar_list'),
    path('tournament_search/', TournamentSearch.as_view(), name='tournament_search'),
    path('tournament_search/<int:pk>/', TournamentDetail.as_view(), name='tournament_detail'),
    path('competitors/', CompetitorSearch.as_view(), name='competitor_search'),
    path('about/', about_us_view, name='about'),
    path('feedback_to_mail/', send_feedback_to_admin, name='feedback_to_admin'),
    path('file_check/<int:pk>/', file_upload_check, name='file_check'),
    path('questions/', QuestionsListView.as_view(), name='questions_list'),
    path('participiant_create/<int:pk>/', ParticipantCreate.as_view(), name='ParticipantCreate'),
    path('player_detail/<int:pk>/recommendation_add/', RecommendationCreateView.as_view(), name='recommendation_add'),
    path('recommendation/<int:pk>/update', RecommendationUpdateView.as_view(), name='recommendation_update'),
    path('recommendation_delete/<int:pk>/', RecommendationDeleteView.as_view(), name='recommendation_delete'),
]
