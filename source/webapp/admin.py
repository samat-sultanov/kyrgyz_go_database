from django.contrib import admin
from accounts.models import User
from webapp.models import Country, City, Club, Game, Tournament, Player, PlayerInTournament

admin.site.register(User)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Club)
admin.site.register(Game)
admin.site.register(Tournament)
admin.site.register(Player)
admin.site.register(PlayerInTournament)

