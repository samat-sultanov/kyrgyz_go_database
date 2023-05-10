import json
import os
from urllib.parse import urlencode

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, DeleteView, FormView
from django.db.models import Q
from webapp.handle_upload import unpack_tournament_to_bd, unpack_countries_clubs, unpack_players, unpack_games
from webapp.views.GoR_calculator import get_new_rating, get_current_rating_and_rank
from webapp.forms import TournamentSearchForm, CheckTournamentForm, CheckPlayerForm
from webapp.models import Tournament, NotModeratedTournament
from django.contrib.auth.mixins import PermissionRequiredMixin
from webapp.views.functions import get_wins_losses, unpack_data_for_moderation_tournament, unpack_data_json_players, \
    parse_results, update_json_tournament
from django.contrib import messages


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
        data = tournament.playerintournament_set.all().order_by('position')

        list_of_rounds = []
        for roundd in range(tournament.rounds):
            list_of_rounds.append(roundd + 1)

        kwargs["tournament"] = tournament
        kwargs['players'] = parse_results(data)
        kwargs['wins'] = get_wins_losses(pk=pk)
        kwargs['list_of_rounds'] = list_of_rounds
        return super().get_context_data(**kwargs)


class TournamentModerationList(PermissionRequiredMixin, ListView):
    model = NotModeratedTournament
    context_object_name = "tournaments"
    template_name = 'tournament/moderation_list.html'
    paginate_by = 10

    def has_permission(self):
        return self.request.user.is_superuser == 1


class DeleteTournamentOnModeration(PermissionRequiredMixin, DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['pk'] = pk
        return context

    def has_permission(self):
        return self.request.user.is_superuser == 1

    def get_success_url(self):
        messages.success(self.request, 'Турнир успешно удален!')
        return reverse_lazy('webapp:moderation_tournaments')

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        tournament = get_object_or_404(NotModeratedTournament, pk=pk)
        file_name = tournament.name
        file_path = f"uploads/json/{file_name.split('.')[0]}.json"
        os.remove(file_path)
        tournament.delete()
        return HttpResponseRedirect(self.get_success_url())


class DeleteTournamentBeforeModeration(PermissionRequiredMixin, TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file_name = self.kwargs.get('file_name')
        file_path = f"uploads/json/{file_name.split('.')[0]}.json"
        context['file_path'] = file_path
        return context

    def has_permission(self):
        return self.request.user.is_superuser == 1

    def get_success_url(self):
        return reverse_lazy('webapp:file_upload')

    def post(self, request, *args, **kwargs):
        file_name = self.kwargs.get('file_name')
        file_path = f"uploads/json/{file_name.split('.')[0]}.json"
        os.remove(file_path)
        return HttpResponseRedirect(self.get_success_url())


class ModerationTournamentView(PermissionRequiredMixin, FormView):
    template_name = 'tournament/moderation_detail.html'
    form_class = CheckTournamentForm
    CheckPlayerFormSet = formset_factory(CheckPlayerForm, extra=0)

    def has_permission(self):
        return self.request.user.is_superuser == 1

    def get_success_url(self):
        if self.form_valid:
            messages.success(self.request, 'Турнир успешно добавлен в базу данных!')
        else:
            messages.error(self.request, 'Турнир не был загружен!')
        return reverse_lazy('webapp:moderation_tournaments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        tournament = get_object_or_404(NotModeratedTournament, pk=pk)
        file_name = tournament.name
        json_file_path = f"json/{file_name.split('.')[0]}.json"
        with default_storage.open(json_file_path, 'r') as f:
            data = json.load(f)
        tournament_data = unpack_data_for_moderation_tournament(data)
        players = unpack_data_json_players(data)
        players_data = parse_results(players)
        list_of_rounds = []
        for i in range(tournament_data.get('NumberOfRounds')):
            list_of_rounds.append(i + 1)
        context['tournament'] = tournament_data
        context['players'] = players_data
        context['list_of_rounds'] = list_of_rounds
        context['pk'] = pk
        context['form1'] = self.form_class(initial=tournament_data)
        context['form2'] = self.CheckPlayerFormSet(initial=players_data)
        return context

    def form_valid(self, form):
        tournament_data = {
            'Name': form.cleaned_data['Name'],
            'NumberOfRounds': form.cleaned_data['NumberOfRounds'],
            'Boardsize': form.cleaned_data['Boardsize'],
            'date': form.cleaned_data['date'].isoformat(),
            'country': form.cleaned_data['country'],
            'region': form.cleaned_data['region'],
            'city': form.cleaned_data['city'],
            'location': form.cleaned_data['location'],
            'tournament_class': form.cleaned_data['tournament_class'],
            'regulations': form.cleaned_data['regulations'],
            'uploaded_by': self.request.user.username
        }
        players_data = []
        for i in range(int(form.data['form-TOTAL_FORMS'])):
            player_data = {
                'EgdPin': form.data[f'form-{i}-EgdPin'],
                'Surname': form.data[f'form-{i}-Surname'],
                'FirstName': form.data[f'form-{i}-FirstName'],
                'birth_date': form.data[f'form-{i}-birth_date'],
                'GoLevel': form.data[f'form-{i}-GoLevel'],
                'Rating': form.data[f'form-{i}-Rating'],
                'id_in_tournament': form.data[f'form-{i}-id_in_tournament'],
                'position': form.data[f'form-{i}-position'],
                'results': form.data[f'form-{i}-results'],
                'Club': form.data[f'form-{i}-Club']
            }
            players_data.append(player_data)
        pk = self.kwargs.get('pk')
        tournament = get_object_or_404(NotModeratedTournament, pk=pk)
        file_name = tournament.name
        json_file_path = f"json/{file_name.split('.')[0]}.json"
        with default_storage.open(json_file_path, 'r') as f:
            data = json.load(f)
            update_data = update_json_tournament(data, tournament_data, players_data)
        json_data = json.dumps(update_data, indent=4)
        with default_storage.open(json_file_path, 'w') as f:
            f.write(ContentFile(json_data).read())
        with default_storage.open(json_file_path, 'r') as f:
            data = json.load(f)
        new_pk = unpack_tournament_to_bd(data)
        unpack_countries_clubs(data)
        unpack_players(data, new_pk)
        unpack_games(data, new_pk)
        tournament.delete()
        file_path = f"uploads/json/{file_name.split('.')[0]}.json"
        os.remove(file_path)
        get_new_rating(new_pk)
        get_current_rating_and_rank(new_pk)
        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        form1 = self.form_class(self.request.POST, initial=context['tournament'], prefix='form1')
        form2 = self.CheckPlayerFormSet(self.request.POST, initial=context['players'], prefix='form')
        context['form1'] = form1
        context['form2'] = form2
        context['form1_errors'] = form.errors
        context['form2_errors'] = formset_errors(form2)
        self.extra_context = context
        return super().form_invalid(form)


def formset_errors(formset):
    errors = [form.errors for form in formset.forms]
    errors = [error for error in errors if error]
    return errors
