import re

from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404

from webapp.models import Club, Country
from django.views.generic import ListView


class ClubsListView(ListView):
    model = Club
    template_name = 'club/club_list.html'
    context_object_name = 'clubs'
    paginate_by = 15
    paginate_orphans = 4

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data'] = self.average_go_level()
        return context

    @staticmethod
    def average_go_level():
        # Здесь нужно будет привязать фильтр через страну клуба, чтобы выводил только по Кыргызстану
        clubs = Club.objects.all()
        club_list = []
        for club in clubs:
            new_dict = dict()
            num_list = []
            num_players = club.players.count()
            for player in club.players.all():
                tournaments = player.playerintournament_set.all()
                for person in tournaments:
                    if person.GoLevel:
                        p = re.compile('(\d*)')
                        m = p.findall(person.GoLevel)
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
