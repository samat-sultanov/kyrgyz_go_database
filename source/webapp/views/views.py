import re
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from webapp.handle_upload import handle_uploaded_file
from webapp.models import File, Calendar, Country, Player, Tournament, News
from webapp.forms import FileForm


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
        calendar = Calendar.objects.order_by('event_date')[:3]
        context['calendar'] = calendar
        players = get_position_in_kgf()[0:3]
        context['position'] = players
        latest_news = News.objects.filter(is_deleted=False).order_by('-created_at')[:3]
        context['latest_news'] = latest_news
        return context


def file_upload(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            a = form.save()
            handle_uploaded_file(request.FILES['file'])
            file = get_object_or_404(File, pk=a.id)
            file.delete()
        else:
            return render(request, 'file_upload.html', {'form': form})
        return HttpResponseRedirect("/")
    else:
        form = FileForm
    return render(request, 'file_upload.html', {'form': form})
