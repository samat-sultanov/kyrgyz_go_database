from django.contrib import admin
from .models import Country, City, Club, Game, Tournament, Player, PlayerInTournament, News, Calendar, Participant

admin.site.register(Country)
admin.site.register(City)
admin.site.register(Club)
admin.site.register(Game)
admin.site.register(Tournament)
admin.site.register(Player)
admin.site.register(News)
admin.site.register(Calendar)
admin.site.register(Participant)

