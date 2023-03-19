import re

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, View
from webapp.handle_upload import handle_uploaded_file
from webapp.models import File, Calendar, Country, Player, Tournament, News, Game
from webapp.forms import FileForm, CheckTournamentForm, CheckPlayerForm, FeedbackToEmailForm
from webapp.views.functions import get_wins_losses


def get_position_in_kgf():
    country = Country.objects.get(country_code='kg')
    players = Player.objects.filter(country=country)
    tournaments = Tournament.objects.order_by("date")
    new_list = []
    for player in players:
        new_dict = dict()
        for tournament in tournaments:
            for data in tournament.playerintournament_set.all():
                if player.pk == data.player_id:
                    if player.pk not in new_dict:
                        new_dict['player'] = player
                        p = re.compile('(\d*)')
                        m = p.findall(data.GoLevel)
                        for i in m:
                            if i != "":
                                new_dict['GoLevel'] = int(i)
        new_list.append(new_dict)
    new_list.sort(key=lambda dictionary: dictionary['GoLevel'])
    position = 1
    for element in new_list:
        element['position'] = position
        position += 1
    return new_list


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
        return context


class QuestionsListView(View):

    def get(self, request):
        if request.method == 'GET':
            return render(request, 'faq/questions_list.html')


def file_upload(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            a = form.save()
            tournament = handle_uploaded_file(request.FILES['file'])
            file = get_object_or_404(File, pk=a.id)
            file.delete()
        else:
            return render(request, 'file_upload.html', {'form': form})
        return redirect('webapp:file_check', pk=tournament.pk)
    else:
        form = FileForm
    return render(request, 'file_upload.html', {'form': form})


def file_upload_check(request, pk):
    if request.method == 'POST':
        tournament = Tournament.objects.get(pk=pk)
        players = tournament.player_set.all()
        patronymic = request.POST.getlist('patronymic')
        birth_date = request.POST.getlist('birth_date')
        tournament_form = CheckTournamentForm(request.POST)
        city = request.POST.get('city')
        date = request.POST.get('date')
        regulations = request.POST.get('regulations')
        tournament_class = request.POST.get('tournament_class')
        uploaded_by = request.user
        if tournament_form.is_valid():
            if city == '' and date == '' and tournament_class == '' and regulations =='':
                tournament_form = CheckTournamentForm({'city': tournament.city, 'date': tournament.date, 'tournament_class':tournament.tournament_class, 'regulations':tournament.regulations, 'uploaded_by': uploaded_by}, instance=tournament)
            else:
                tournament_form = CheckTournamentForm({'city': city, 'date': date, 'tournament_class':tournament_class, 'regulations':regulations, 'uploaded_by': uploaded_by}, instance=tournament)
            tournament_form.save()

        form = CheckPlayerForm(request.POST)
        if form.is_valid():
            for player, patron, bd in zip(players, patronymic, birth_date):
                print(player, patron, bd)
                if patron == '' and bd == '':
                    form = CheckPlayerForm({'patronymic': player.patronymic, 'birth_date': player.birth_date},
                                           instance=player)
                elif patron == '' and bd != '':
                    form = CheckPlayerForm({'patronymic': player.patronymic, 'birth_date': bd}, instance=player)
                elif patron != '' and bd == '':
                    form = CheckPlayerForm({'patronymic': patron, 'birth_date': player.birth_date}, instance=player)
                else:
                    form = CheckPlayerForm({'patronymic': patron, 'birth_date': bd}, instance=player)
                form.save()
            return redirect(reverse('webapp:tournament_detail', kwargs={'pk': tournament.pk}))
        else:
            return render(request, 'webapp:file_upload.html', {'form': form})

    if request.method == 'GET':
        tournament = Tournament.objects.get(pk=pk)
        players = tournament.player_set.all()
        player_form = CheckPlayerForm()
        tournament_form = CheckTournamentForm()
        wins = get_wins_losses(pk)
        return render(request, 'tournament/tournament_check.html',
                      {'tournament': tournament, 'players': players, 'wins': wins, 'player_form': player_form,
                       'tournament_form': tournament_form})


def about_us_view(request, *args, **kwargs):
    if request.method == 'GET':
        form = FeedbackToEmailForm()
        context = {'form': form}
        return render(request, 'about_us.html', context)


def send_feedback_to_admin(request, *args, **kwargs):
    if request.method == 'POST':
        admin = get_user_model().objects.all().get(pk=1)
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
                send_mail(subject, message, admin.email, [admin.email, ])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect("webapp:about")
