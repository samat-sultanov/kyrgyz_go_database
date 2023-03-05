from urllib.parse import urlencode
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, TemplateView
from django.db.models import Q

from webapp.forms import TournamentSearchForm
from webapp.models import Tournament


class TournamentSearch(ListView):
    template_name = 'tournament/tournament_search.html'
    context_object_name = 'tournaments'
    model = Tournament
    ordering = ['-date']
    paginate_by = 5

    def get(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.search_name = self.get_search_name()
        self.search_city = self.get_search_city()
        self.search_date = self.get_search_date()
        self.search_tournament_class = self.get_search_tournament_class()
        return super().get(request, *args, **kwargs)

    def get_search_form(self):
        return TournamentSearchForm(self.request.GET)

    def get_search_name(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_name']

    def get_search_city(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_city']

    def get_search_date(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_date']

    def get_search_tournament_class(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_tournament_class']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.search_name:
            queryset = queryset.filter(Q(name__icontains=self.search_name))
        if self.search_city:
            queryset = queryset.filter(Q(city__city__icontains=self.search_city))
        if self.search_date:
            queryset = queryset.filter(Q(date=self.search_date))
        if self.search_tournament_class and self.search_tournament_class != 'all':
            queryset = queryset.filter(Q(tournament_class__exact=self.search_tournament_class))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'] = self.form
        if self.search_name:
            context['query'] = urlencode({'search_name': self.search_name})
            context['search_name'] = self.search_name
        elif self.search_city:
            context['query'] = urlencode({'search_city': self.search_city})
            context['search_city'] = self.search_city
        elif self.search_date:
            context['query'] = urlencode({'search_date': self.search_date})
            context['search_date'] = self.search_date
        elif self.search_tournament_class:
            context['query'] = urlencode({'search_tournament_class': self.search_tournament_class})
            context['search_tournament_class'] = self.search_tournament_class
        return context


class TournamentDetail(TemplateView):
    template_name = 'tournament/tournament_detail.html'

    def get_context_data(self, **kwargs):
        pk = kwargs.get("pk")
        tournament = get_object_or_404(Tournament, pk=pk)
        players = tournament.player_set.all()
        kwargs["tournament"] = tournament
        kwargs['players'] = players
        return super().get_context_data(**kwargs)
