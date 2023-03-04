from django.shortcuts import render
from django.views import View

from webapp.forms import TournamentSearchForm


class TournamentSearch(View):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'tournament/tournament_search.html', {'form': TournamentSearchForm})
