from webapp.models import Player, City
from rest_framework import serializers

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'city')
        read_only_fields = ['id']

class PlayerSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'current_rank', 'city']
        read_only_fields = ['id']