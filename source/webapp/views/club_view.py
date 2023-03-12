import re
from urllib.parse import urlencode

from django.db.models import Q
from django.shortcuts import get_object_or_404
from webapp.forms import ClubSearch
from webapp.models import Club, Country, PlayerInTournament
from django.views.generic import ListView, TemplateView


def average_go_level():
    # Здесь нужно будет привязать фильтр через страну клуба, чтобы выводил только по Кыргызстану
    clubs = Club.objects.all()
    club_list = []
    for club in clubs:
        new_dict = dict()
        num_list = []
        num_players = club.players.count()
        for player in club.players.all():
            tournament = player.tournaments.all().order_by('-date')[:1]
            data = player.playerintournament_set.get(tournament_id=tournament)
            if data.GoLevel:
                p = re.compile('(\d*)')
                m = p.findall(data.GoLevel)
                for i in m:
                    if i != "":
                        num_list.append(int(i))
        total_go_level = sum(num_list)
        if num_players > 0:
            average_num = total_go_level // num_players
            new_dict['club'] = club.pk
            new_dict['average'] = average_num
        else:
            new_dict['club'] = club.pk
            new_dict['average'] = 0
        club_list.append(new_dict)
    return club_list


class ClubsListView(ListView):
    model = Club
    template_name = 'club/club_list.html'
    context_object_name = 'clubs'
    paginate_by = 15
    paginate_orphans = 4

    def get(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.search_name = self.get_search_name()
        self.search_city = self.get_search_city()
        return super().get(request, *args, **kwargs)

    def get_search_form(self):
        return ClubSearch(self.request.GET)

    def get_search_name(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_name']

    def get_search_city(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_city']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.search_name:
            queryset = queryset.filter(Q(name__icontains=self.search_name))
        if self.search_city:
            queryset = queryset.filter(Q(city__city__icontains=self.search_city))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        # context = super().get_context_data(**kwargs)
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'] = self.form
        context['data'] = average_go_level()
        if self.search_name:
            context['query'] = urlencode({'search_name': self.search_name})
            context['search_name'] = self.search_name
        elif self.search_city:
            context['query'] = urlencode({'search_city': self.search_city})
            context['search_city'] = self.search_city
        return context


class ClubView(TemplateView):
    template_name = 'club/club_detail.html'

    def get_context_data(self, **kwargs):
        pk = kwargs.get("pk")
        club = get_object_or_404(Club, pk=pk)
        players = club.players.all()
        kwargs["club"] = club
        kwargs['players'] = players
        new_list = []
        for player in players:
            new_dict = dict()
            tournament = player.tournaments.all().order_by('-date')[:1]
            data = player.playerintournament_set.get(tournament_id=tournament)
            new_dict['player'] = player.pk
            new_dict['GoLevel'] = data.GoLevel
            new_list.append(new_dict)
        kwargs['rating'] = new_list
        kwargs['num_participants'] = club.players.count
        club_list = average_go_level()
        for element in club_list:
            if club.pk == element['club']:
                kwargs['average'] = element['average']
        return super().get_context_data(**kwargs)