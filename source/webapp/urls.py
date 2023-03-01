from django.urls import path
from .views import file_upload, IndexView

app_name = 'webapp'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('file_upload/', file_upload , name='file_upload')
]