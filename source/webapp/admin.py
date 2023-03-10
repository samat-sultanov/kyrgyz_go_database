from django.contrib import admin
from accounts.models import User
from .models import Country, City, Club, Game, Tournament, Player, PlayerInTournament, News


class PlayerInTournamentAdmin(admin.ModelAdmin):
    list_display = ['game_id', 'player', 'tournament', 'GoLevel', 'rating']


admin.site.register(PlayerInTournament, PlayerInTournamentAdmin)
admin.site.register(User)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Club)
admin.site.register(Game)
admin.site.register(Tournament)
admin.site.register(Player)
admin.site.register(News)
