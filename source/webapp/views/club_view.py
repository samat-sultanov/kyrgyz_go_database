from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from webapp.forms import ClubSearch, ClubForm, ClubCreateForm
from webapp.models import Club, Country
from django.views.generic import ListView, TemplateView, UpdateView, CreateView
from webapp.views.functions import average_go_level, get_total_wins


class ClubsListView(ListView):
    model = Club
    template_name = 'club/club_list.html'
    context_object_name = 'clubs'
    paginate_by = 15
    paginate_orphans = 4
    country = Country.objects.get(country_code='kg')
    queryset = Club.objects.filter(country=country)

    def get_ordering(self):
        ordering = '-num_players'
        if self.request.GET.get('ordering'):
            ordering = self.request.GET.get('ordering')
        return ordering

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
            queryset = queryset.filter(Q(name__startswith=self.search_name))
        if self.search_city:
            queryset = queryset.filter(Q(city__city__startswith=self.search_city))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'] = self.form
        context['data'] = average_go_level()
        country = Country.objects.get(country_code='kg')
        clubs = Club.objects.filter(country=country)
        context['wins'] = get_total_wins(clubs)
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
        club_list = average_go_level()
        for element in club_list:
            if club.pk == element['club']:
                kwargs['average'] = element['average']
        return super().get_context_data(**kwargs)


class ClubUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'club/club_update.html'
    model = Club
    form_class = ClubForm

    def get_success_url(self):
        return reverse('webapp:club_view', kwargs={'pk': self.object.pk})

class ClubCreate(LoginRequiredMixin, CreateView):
    template_name = 'club/club_create.html'
    model = Club
    form_class = ClubCreateForm

    def get_success_url(self):
        return reverse('webapp:index')