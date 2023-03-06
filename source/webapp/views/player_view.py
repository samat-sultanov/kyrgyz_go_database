import datetime
import re
from urllib.parse import urlencode

from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from webapp.models import Player, Country, Tournament
from webapp.forms import FileForm, PlayerSearchForm, CompetitorSearchForm
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class PlayerDetail(DetailView):
    template_name = 'player_search/player_detail.html'
    model = Player


class PlayerSearch(ListView):
    template_name = 'player_search/player_search.html'
    context_object_name = 'players'
    model = Player
    ordering = ['first_name']
    paginate_by = 15
    paginate_orphans = 4

    def get(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.search_name = self.get_search_name()
        self.search_patronymic = self.get_search_patronymic()
        self.search_last_name = self.get_search_last_name()
        self.search_clubs = self.get_search_clubs()
        self.search_city = self.get_search_city()
        return super().get(request, *args, **kwargs)

    def get_search_form(self):
        return PlayerSearchForm(self.request.GET)

    def get_search_name(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_first_name']

    def get_search_patronymic(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_patronymic']

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
        if self.search_patronymic:
            queryset = queryset.filter(Q(patronymic__icontains=self.search_patronymic))
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
        elif self.search_patronymic:
            context['query'] = urlencode({'search_patronymic': self.search_patronymic})
            context['search_patronymic'] = self.search_patronymic
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


class CompetitorSearch(View):

    def get(self, request):
        if request.method == "GET":
            return render(request, 'competitor/competitor_search.html', {'form': CompetitorSearchForm})

