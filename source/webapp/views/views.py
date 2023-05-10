import xmltodict
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.forms import formset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from webapp.models import Calendar, News, Partner, NotModeratedTournament, Tournament
from webapp.forms import FileForm, CheckTournamentForm, CheckPlayerForm, FeedbackToEmailForm
from webapp.views.functions import get_position_in_kgf, unpack_data_json_tournament, unpack_data_json_players, \
    update_json_tournament


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


class FileUpload(LoginRequiredMixin, FormView):
    template_name = 'file_upload.html'
    form_class = FileForm

    def form_valid(self, form):
        xml_file = self.request.FILES['file']
        file_name = xml_file.name.strip().split('.')[0].lower().replace(' ', '_')
        file_ext = xml_file.name.split('.')[-1].lower()
        if file_ext != 'xml':
            form.add_error(None, 'Действие отклонено! К загрузке доступны только файлы с расширением Xml!')
            return render(self.request, self.template_name, {'form': form, 'error': form.errors})
        json_file_path = f'json/{file_name}.json'
        if default_storage.exists(json_file_path):
            form.add_error(None, 'Действие отклонено! Файл с таким именем уже был загружен!')
            return render(self.request, self.template_name, {'form': form, 'error': form.errors})
        doc = xmltodict.parse(xml_file)
        data = doc['Tournament']
        for key, value in data.items():
            if key == 'Name':
                name = value
                try:
                    Tournament.objects.get(name=name)
                    form.add_error(None, 'Действие отклонено! Турнир с таким именем уже есть в базе данных!')
                    return render(self.request, self.template_name, {'form': form, 'error': form.errors})
                except:
                    json_data = json.dumps(doc, indent=4)
                    with default_storage.open(json_file_path, 'w') as f:
                        f.write(ContentFile(json_data).read())
                    xml_file.file.close()
        return HttpResponseRedirect(reverse('webapp:file_check', args=[file_name]))


class TournamentCheckView(LoginRequiredMixin, FormView):
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
            'country': form.cleaned_data.get('country', ''),
            'region': form.cleaned_data.get('region', 0),
            'city': form.cleaned_data.get('city', 0),
            'tournament_class': form.cleaned_data['tournament_class'],
            'regulations': form.cleaned_data['regulations'],
            'location': form.cleaned_data['location'],
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
        file_name = self.kwargs.get('file_name')
        json_file_path = f"json/{file_name.split('.')[0]}.json"
        with default_storage.open(json_file_path, 'r') as f:
            data = json.load(f)
            update_data = update_json_tournament(data, tournament_data, players_data)
        json_data = json.dumps(update_data, indent=4)
        with default_storage.open(json_file_path, 'w') as f:
            f.write(ContentFile(json_data).read())
        NotModeratedTournament.objects.create(name=file_name, uploaded_by=self.request.user)
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
