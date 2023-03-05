from django.db.models import Count

from webapp.models import Club
from django.views.generic import ListView


class ClubsListView(ListView):
    model = Club
    template_name = 'club/club_list.html'
    context_object_name = 'clubs'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(num_players=Count('club_players')).order_by('-num_players')
        return queryset
