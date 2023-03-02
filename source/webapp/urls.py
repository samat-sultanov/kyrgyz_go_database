from django.urls import path
from .views import file_upload, NewsListView

app_name = 'webapp'

urlpatterns = [
    path('file_upload/', file_upload, name='file_upload'),
    path('news/', NewsListView.as_view(), name='news_list'),
]