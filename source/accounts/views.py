from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView
from webapp.models import Player


class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'user_detail.html'
    context_object_name = 'user_obj'

    def get_context_data(self, **kwargs):
        if kwargs['object'].pk == 1 and not self.request.user.is_superuser:
            raise PermissionDenied()
        else:
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
            data = Player.objects.filter(pk__in=coach_students)
            context['players'] = data
            return context
