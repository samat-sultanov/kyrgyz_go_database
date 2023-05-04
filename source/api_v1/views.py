import json

from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters

from webapp.models import Player, City, Region, Country
from api_v1.serializers import PlayerSerializer


class PlayerSerView(ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    filter_backends = [filters.SearchFilter]
    permission_classes = [IsAdminUser]
    filterset_fields = ['last_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_params = self.request.query_params.get('last_name', None)

        if not filter_params:
            return Player.objects.none()

        return queryset.filter(Q(last_name__startswith=filter_params))

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()


@ensure_csrf_cookie
def get_token_view(request, *args, **kwargs):
    if request.method == 'GET':
        return HttpResponse()
    return HttpResponseNotAllowed(['GET'])


def get_region(request, *args, **kwargs):
    if request.method == "POST":
        if request.body:
            received = json.loads(request.body)
            country = received.get("country")
            print(country)
