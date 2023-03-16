import re
from urllib.parse import urlencode
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from webapp.forms import ClubSearch, ClubForm
from webapp.models import Club
from django.views.generic import ListView, TemplateView, UpdateView
from webapp.views.functions import get_list_of_filtered_players, get_rank, average_go_level, sorted_list_of_players


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
        data = get_rank(players)
        sorted_players = get_list_of_filtered_players(data, sorted_list_of_players)
        kwargs["club"] = club
        kwargs['players'] = sorted_players
        club_list = average_go_level()
        for element in club_list:
            if club.pk == element['club']:
                kwargs['average'] = element['average']
        return super().get_context_data(**kwargs)


class ClubUpdate(UpdateView):
    template_name = 'club/club_update.html'
    model = Club
    form_class = ClubForm

    def get_success_url(self):
        return reverse('webapp:club_view', kwargs={'pk': self.object.pk})