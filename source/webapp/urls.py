from django.urls import path
from .views import file_upload

app_name = 'webapp'

urlpatterns = [
    path('file_upload/', file_upload , name='file_upload')
]