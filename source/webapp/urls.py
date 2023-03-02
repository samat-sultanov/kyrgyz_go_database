from django.urls import path
<<<<<<< HEAD
from .views import file_upload, IndexView
=======
from .views import file_upload, NewsListView
>>>>>>> dev

app_name = 'webapp'

urlpatterns = [
<<<<<<< HEAD
    path('', IndexView.as_view(), name='index'),
    path('file_upload/', file_upload , name='file_upload')
=======
    path('file_upload/', file_upload, name='file_upload'),
    path('news/', NewsListView.as_view(), name='news_list'),
>>>>>>> dev
]