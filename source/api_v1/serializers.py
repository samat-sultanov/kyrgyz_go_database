from webapp.models import Player
from rest_framework import serializers


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'patronymic', 'first_name', 'last_name', 'current_rank']
        read_only_fields = ['id']