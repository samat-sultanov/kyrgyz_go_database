from django.contrib.auth import get_user_model
from django.views.generic import DetailView

from webapp.models import Player
from webapp.views.functions import get_rank, get_list_of_filtered_players


class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'user_detail.html'
    context_object_name = 'user_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        coach = self.get_object()
        coach_clubs = []
        coach_students = []
        for club in coach.clubs.all():
            coach_clubs.append(club.pk)
        for player in Player.objects.all():
            for each_club in player.clubs.all():
                if each_club.pk in coach_clubs:
                    coach_students.append(player.pk)
        data = get_rank(Player.objects.filter(pk__in=coach_students))
        sorted_players = get_list_of_filtered_players(data)
        context['players'] = sorted_players
        return context
