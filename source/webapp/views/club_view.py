from django.db.models import Avg, Count

from webapp.models import Club
from django.views.generic import ListView


class ClubsListView(ListView):
    model = Club
    template_name = 'club/club_list.html'
    context_object_name = 'clubs'
    paginate_by = 15
    paginate_orphans = 4

