from django.urls import path, include
from api_v1.views import PlayerSerView, get_token_view, get_region
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'api_v1'

router = DefaultRouter()
router.register('player', PlayerSerView)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>', include(router.urls)),
    path('get_token/', get_token_view),
    path('login/', obtain_auth_token, name='api_token_auth'),
    path('get_regions/', get_region, name='get_regions'),
]
