from urllib.parse import urlencode
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from webapp.models import Player
from webapp.forms import PlayerSearchForm, CompetitorSearchForm, PlayerForm
from django.views.generic import ListView, UpdateView, DeleteView, TemplateView
from django.urls import reverse
from webapp.views.functions import get_position_in_kgf, get_rating_from_rank


class PlayerDetail(TemplateView):
    context_key = 'player'
    key_kwarg = 'pk'
    template_name = 'player/player_detail.html'
    model = Player

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.context_key] = self.get_object()
        context['position'] = get_position_in_kgf()
        return context

    def get_object(self):
        pk = self.kwargs.get(self.key_kwarg)
        return get_object_or_404(self.model, pk=pk)


class PlayerSearch(ListView):
    template_name = 'player/player_search.html'
    context_object_name = 'players'
    queryset = Player.objects.order_by('-current_rating')
    model = Player
    paginate_by = 15
    paginate_orphans = 4

    def get(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.search_name = self.get_search_name()
        self.search_last_name = self.get_search_last_name()
        self.search_clubs = self.get_search_clubs()
        self.search_city = self.get_search_city()
        return super().get(request, *args, **kwargs)

    def get_search_form(self):
        return PlayerSearchForm(self.request.GET)

    def get_search_name(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_first_name']

    def get_search_last_name(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_last_name']

    def get_search_clubs(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_clubs']

    def get_search_city(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_city']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.search_name:
            queryset = queryset.filter(Q(first_name__icontains=self.search_name))
        if self.search_last_name:
            queryset = queryset.filter(Q(last_name__icontains=self.search_last_name))
        if self.search_clubs:
            queryset = queryset.filter(Q(clubs__name__icontains=self.search_clubs))
        if self.search_city:
            queryset = queryset.filter(Q(city__city__icontains=self.search_city))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'] = self.form
        if self.search_name:
            context['query'] = urlencode({'search_first_name': self.search_name})
            context['search_first_name'] = self.search_name
        elif self.search_last_name:
            context['query'] = urlencode({'search_last_name': self.search_last_name})
            context['search_last_name'] = self.search_last_name
        elif self.search_clubs:
            context['query'] = urlencode({'search_clubs': self.search_clubs})
            context['search_clubs'] = self.search_clubs
        elif self.search_city:
            context['query'] = urlencode({'search_city': self.search_city})
            context['search_city'] = self.search_city
        return context


class UpdatePlayer(PermissionRequiredMixin, UpdateView):
    template_name = 'player/update_player.html'
    model = Player
    form_class = PlayerForm
    permission_required = ('webapp.change_player',)

    def get_success_url(self):
        return reverse('webapp:player_detail', kwargs={'pk': self.object.pk})


class DeletePlayer(PermissionRequiredMixin, DeleteView):
    model = Player
    permission_required = ('webapp.delete_player',)

    def get_success_url(self):
        return reverse('webapp:player_search')


class CompetitorSearch(ListView):
    template_name = 'competitor/competitor_search.html'
    context_object_name = 'players'
    model = Player
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.search_rank = self.get_search_rank()
        self.search_clubs = self.get_search_clubs()
        self.search_city = self.get_search_city()
        self.search_country = self.get_search_country()
        return super().get(request, *args, **kwargs)

    def get_search_form(self):
        return CompetitorSearchForm(self.request.GET)

    def get_search_rank(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_rank']

    def get_search_clubs(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_clubs']

    def get_search_city(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_city']

    def get_search_country(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_country']

    def get_queryset(self):
        queryset = super().get_queryset()
        rating = get_rating_from_rank(self.search_rank)
        if self.search_rank:
            queryset = queryset.filter(Q(current_rating__range=(rating-300, rating+300)))
        if self.search_clubs:
            queryset = queryset.filter(Q(clubs__name__icontains=self.search_clubs))
        if self.search_city:
            queryset = queryset.filter(Q(city__city__icontains=self.search_city))
        if self.search_country:
            queryset = queryset.filter(Q(country__country_code__icontains=self.search_country))  # check
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'] = self.form
        if self.search_rank:
            context['query'] = urlencode({'search_rank': self.search_rank})
            context['search_rank'] = self.search_rank
        elif self.search_clubs:
            context['query'] = urlencode({'search_clubs': self.search_clubs})
            context['search_clubs'] = self.search_clubs
        elif self.search_city:
            context['query'] = urlencode({'search_city': self.search_city})
            context['search_city'] = self.search_city
        elif self.search_country:
            context['query'] = urlencode({'search_country': self.search_country})
            context['search_country'] = self.search_country
        return context
