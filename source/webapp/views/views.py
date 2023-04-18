import os
from xml.etree.ElementTree import fromstring

import lxml
import xmltodict
import json

from bs4 import BeautifulSoup
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.forms import formset_factory
from django.http import HttpResponse, FileResponse, HttpResponseRedirect, HttpResponseBadRequest, request
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.html import strip_tags
from django.views import View
from django.views.generic import TemplateView, FormView
from webapp.handle_upload import handle_uploaded_file
from webapp.models import File, Calendar, Tournament, News, Partner
from webapp.forms import FileForm, CheckTournamentForm, CheckPlayerForm, FeedbackToEmailForm
from webapp.views.GoR_calculator import get_new_rating
from webapp.views.functions import get_wins_losses, get_position_in_kgf, \
    unpack_data_json_tournament, unpack_data_json_players, update_json_tournament
from django.core.exceptions import PermissionDenied
from django import forms
from django.contrib import messages


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.filter(is_deleted=False).order_by('event_date')
        context['calendar'] = calendar
        players = get_position_in_kgf()[0:3]
        context['position'] = players
        latest_news = News.objects.filter(is_deleted=False).order_by('-created_at')[:3]
        context['latest_news'] = latest_news
        partners = Partner.objects.all()
        context['partners'] = partners
        return context


class FileUpload(FormView):
    template_name = 'file_upload.html'
    form_class = FileForm

    def form_valid(self, form):
        xml_file = self.request.FILES['file']
        file_name = xml_file.name.strip().split('.')[0].lower().replace(' ', '_')
        file_ext = xml_file.name.split('.')[-1].lower()
        if file_ext != 'xml':
            form.add_error('file', 'Only XML files are allowed.')
            return self.form_invalid(form)
        json_file_path = f'json/{file_name}.json'
        if default_storage.exists(json_file_path):
            form.add_error('file', 'A file with this name already exists.')
            return self.form_invalid(form)
        doc = xmltodict.parse(xml_file)
        json_data = json.dumps(doc, indent=4)
        with default_storage.open(json_file_path, 'w') as f:
            f.write(ContentFile(json_data).read())
        xml_file.file.close()
        return HttpResponseRedirect(reverse('webapp:file_check', args=[file_name]))


class TournamentCheckView(FormView):
    template_name = 'tournament/tournament_check.html'
    form_class = CheckTournamentForm
    CheckPlayerFormSet = formset_factory(CheckPlayerForm, extra=0)
    success_url = '/file_upload/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        file_name = self.kwargs.get('file_name')
        json_file_path = f"json/{file_name.split('.')[0]}.json"
        with default_storage.open(json_file_path, 'r') as f:
            data = json.load(f)
        tournament_data = unpack_data_json_tournament(data)
        players_data = unpack_data_json_players(data)
        context['tournament'] = tournament_data
        context['players'] = players_data
        context['file_name'] = file_name
        context['form1'] = self.form_class(initial=tournament_data)
        context['form2'] = self.CheckPlayerFormSet(initial=players_data)
        return context

    def form_valid(self, form):
        tournament_data = {
            'Name': form.cleaned_data['Name'],
            'NumberOfRounds': form.cleaned_data['NumberOfRounds'],
            'Boardsize': form.cleaned_data['Boardsize'],
            'date': form.cleaned_data['date'].isoformat(),
            'city': form.cleaned_data['city'],
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
                'id_in_game': form.data[f'form-{i}-id_in_game']
            }
            players_data.append(player_data)
        file_name = self.kwargs.get('file_name')
        json_file_path = f"json/{file_name.split('.')[0]}.json"
        with default_storage.open(json_file_path, 'r') as f:
            data = json.load(f)
            update_json_tournament(data, tournament_data, players_data)
        json_data = json.dumps(data, indent=4)
        with default_storage.open(json_file_path, 'w') as f:
            f.write(ContentFile(json_data).read())
        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        form1 = context['form1']
        form2 = context['form2']
        if not form1.is_valid():
            return self.render_to_response(self.get_context_data(form1=form1, form2=form2))
        if not form2.is_valid():
            return self.render_to_response(self.get_context_data(form1=form1, form2=form2))


# def file_upload(request):
#     if request.method == 'POST' and request.user.is_authenticated:
#         form = FileForm(request.POST, request.FILES)
#         if form.is_valid():
#             a = form.save()
#             tournament = handle_uploaded_file(request.FILES['file'])
#             file = get_object_or_404(File, pk=a.id)
#             file.delete()
#             if not tournament:
#                 error = "Действие недоступно! Турнир с таким именем уже есть в базе данных."
#                 return render(request, 'file_upload.html', {'form': form, 'error': error})
#         else:
#             return render(request, 'file_upload.html', {'form': form})
#         return redirect('webapp:file_check', pk=tournament.pk)
#     elif request.method == 'GET' and request.user.is_authenticated:
#         form = FileForm
#         return render(request, 'file_upload.html', {'form': form})
#     else:
#         return render(request, '403.html')
#
#
# def file_upload_check(request, pk):
#     if request.method == 'POST' and request.user.is_authenticated:
#         tournament = Tournament.objects.get(pk=pk)
#         players = tournament.player_set.all()
#         birth_date = request.POST.getlist('birth_date')
#         EgdPin = request.POST.getlist('EgdPin')
#         tournament_form = CheckTournamentForm(request.POST)
#         city = request.POST.get('city')
#         date = request.POST.get('date')
#         regulations = request.POST.get('regulations')
#         tournament_class = request.POST.get('tournament_class')
#         uploaded_by = request.user
#         if tournament_form.is_valid():
#             if city == '' and date == '' and tournament_class == '' and regulations == '':
#                 tournament_form = CheckTournamentForm(
#                     {'city': tournament.city, 'date': tournament.date, 'tournament_class': tournament.tournament_class,
#                      'regulations': tournament.regulations, 'uploaded_by': uploaded_by}, instance=tournament)
#             else:
#                 tournament_form = CheckTournamentForm(
#                     {'city': city, 'date': date, 'tournament_class': tournament_class, 'regulations': regulations,
#                      'uploaded_by': uploaded_by}, instance=tournament)
#             tournament_form.save()
#
#         form = CheckPlayerForm(request.POST)
#         if form.is_valid():
#             try:
#                 for player, pin, bd in zip(players, EgdPin, birth_date):
#                     if bd == '' and pin == '':
#                         form = CheckPlayerForm({'birth_date': player.birth_date, 'EgdPin': player.EgdPin},
#                                                instance=player)
#                     elif bd == '' and pin != '':
#                         form = CheckPlayerForm({'birth_date': player.birth_date, 'EgdPin': pin},
#                                                instance=player)
#                     elif bd != '' and pin == '':
#                         form = CheckPlayerForm({'birth_date': bd, 'EgdPin': player.EgdPin},
#                                                instance=player)
#                     else:
#                         form = CheckPlayerForm({'birth_date': bd, 'EgdPin': pin}, instance=player)
#                     if form.is_valid():
#                         form.save()
#                     else:
#                         messages.add_message(request, messages.ERROR,
#                                              'Поле даты рождения была некорректна заполнена! Отредактируйте данное поле.')
#                         return redirect(request.META.get('HTTP_REFERER'))
#                 return redirect(reverse('webapp:tournament_detail', kwargs={'pk': tournament.pk}))
#             except forms.ValidationError:
#                 messages.add_message(request, messages.ERROR,
#                                      'Поле даты рождения была некорректна заполнена! Отредактируйте данное поле.')
#                 return redirect(request.META.get('HTTP_REFERER'))
#         else:
#             messages.add_message(request, messages.ERROR,
#                                  'Поле даты рождения была некорректна заполнена! Отредактируйте данное поле.')
#             return redirect(request.META.get('HTTP_REFERER'))
#
#     if request.method == 'GET' and request.user.is_authenticated:
#         tournament = Tournament.objects.get(pk=pk)
#         players = tournament.player_set.all()
#         player_form = CheckPlayerForm()
#         tournament_form = CheckTournamentForm()
#         wins = get_wins_losses(pk)
#         return render(request, 'tournament/tournament_check.html',
#                       {'tournament': tournament, 'players': players, 'wins': wins, 'player_form': player_form,
#                        'tournament_form': tournament_form})
#     else:
#         raise PermissionDenied()


def about_us_view(request, *args, **kwargs):
    if request.method == 'GET':
        form = FeedbackToEmailForm()
        context = {'form': form}
        return render(request, 'about_us.html', context)


def send_feedback_to_admin(request, *args, **kwargs):
    if request.method == 'POST':
        form = FeedbackToEmailForm(request.POST)
        if form.is_valid():
            subject = "Сообщение из формы отбратной связи с сайта kgf.kg"
            body = {
                'first_name': form.cleaned_data.get('first_name', None),
                'last_name': form.cleaned_data.get('last_name', None),
                'email': form.cleaned_data.get('email', None),
                'phone_number': form.cleaned_data.get('phone_number', 'Номера нет'),
                'message': form.cleaned_data['message'],
            }
            message = "\n".join(body.values())

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect("webapp:about")
