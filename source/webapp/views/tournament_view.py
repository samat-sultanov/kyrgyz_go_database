from urllib.parse import urlencode
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView, DeleteView
from django.db.models import Q

from webapp.views.GoR_calculator import get_new_rating
from webapp.forms import TournamentSearchForm
from webapp.models import Tournament
from django.contrib.auth.mixins import LoginRequiredMixin
from webapp.views.functions import get_wins_losses


class TournamentSearch(ListView):
    template_name = 'tournament/tournament_search.html'
    context_object_name = 'tournaments'
    model = Tournament
    ordering = ['-date']
    paginate_by = 5

    def get(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        if not self.form.is_valid():
            error = "Дата турнира была некорректно введена! Введите дату турнира в корректном формате."
            return render(request, 'tournament/tournament_search.html',
                          {'form': self.get_search_form(), 'error': error})
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
            queryset = queryset.filter(Q(name__istartswith=self.search_name))
        if self.search_city:
            queryset = queryset.filter(Q(city__city__istartswith=self.search_city))
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
        data = tournament.playerintournament_set.all().order_by('-rating_after')
        kwargs["tournament"] = tournament
        kwargs['sorted_players'] = data
        kwargs['wins'] = get_wins_losses(pk=pk)
        return super().get_context_data(**kwargs)


class TournamentModerationList(ListView, LoginRequiredMixin):
    model = Tournament
    context_object_name = "tournaments"
    template_name = 'tournament/moderation_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(Q(is_moderated=False))
        return queryset


class CheckModer(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        tournament = get_object_or_404(Tournament, pk=self.kwargs.get('pk'))
        tournament.is_moderated = True
        tournament.save()
        get_new_rating(tournament.pk)
        response = JsonResponse({'status': tournament.is_moderated})
        return response


class CheckCancelModer(DeleteView, LoginRequiredMixin):
    queryset = Tournament.objects.all()
    context_object_name = 'Tournament'
    success_url = reverse_lazy('webapp:moderation_tournaments')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class DeleteTournamentBeforeModeration(DeleteView, LoginRequiredMixin):
    queryset = Tournament.objects.all()
    context_object_name = 'Tournament'
    success_url = reverse_lazy('webapp:file_upload')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)
