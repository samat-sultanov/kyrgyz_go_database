import json
from urllib.parse import urlencode

from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from webapp.models import Calendar, Participant, Player
from webapp.forms import CalendarForm, CalendarBulkDeleteForm, ParticipantForm, Search_Par_Player
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView, FormView, View


class CalendarDetailView(TemplateView):
    template_name = 'calendar/calendar_view.html'

    def get_context_data(self, **kwargs):
        pk = kwargs.get('pk')
        event = get_object_or_404(Calendar, pk=pk)
        kwargs['event'] = event
        return super().get_context_data(**kwargs)


class CalendarCreateView(CreateView):
    template_name = 'calendar/calendar_create.html'
    model = Calendar
    form_class = CalendarForm

    def get_success_url(self):
        return reverse('webapp:index')


class CalendarUpdateView(UpdateView):
    template_name = 'calendar/calendar_update.html'
    model = Calendar
    form_class = CalendarForm

    def get_success_url(self):
        return reverse('webapp:index')


class CalendarDeleteView(DeleteView):
    queryset = Calendar.objects.all().filter(is_deleted=False)
    context_object_name = 'event'
    success_url = reverse_lazy('webapp:index')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.is_deleted = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class DeletedCalendarListView(FormView):
    form_class = CalendarBulkDeleteForm
    template_name = 'calendar/calendar_deleted_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deleted_calendar_list'] = Calendar.objects.all().filter(is_deleted=True).order_by('event_date')
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['checkboxes'].queryset = Calendar.objects.all().filter(is_deleted=True).order_by('event_date')
        return form

    def form_valid(self, form):
        selected_to_delete = Calendar.objects.filter(pk__in=list(map(int, self.request.POST.getlist('checkboxes'))))
        print(selected_to_delete)
        selected_to_delete.delete()
        return HttpResponseRedirect(reverse_lazy('webapp:deleted_calendar_list'))


def restore_one_deleted_event(request, *args, **kwargs):
    if request.method == 'GET':
        event = get_object_or_404(Calendar, pk=kwargs.get('pk'))
        event.is_deleted = False
        event.save()
        return redirect('webapp:deleted_calendar_list')


def hard_delete_one_event(request, *args, **kwargs):
    if request.method == 'POST':
        event = get_object_or_404(Calendar, pk=kwargs.get('pk'))
        event.delete()
        return redirect('webapp:deleted_calendar_list')

class ParticipantCreate(CreateView):
    template_name = 'calendar/participiantcreate.html'
    form_class = ParticipantForm
    ordering = ['first_name']

    def form_valid(self, form):
        event = get_object_or_404(Calendar, pk=self.kwargs.get('pk'))
        form.instance.event = event
        return super().form_valid(form)

    def get_search_form(self):
        return Search_Par_Player(self.request.GET)

    def get(self, request, *args, **kwargs):
        self.form = self.get_search_form()
        self.search = self.get_search()
        self.player = self.get_players()
        return super().get(request, *args, **kwargs)

    def get_search(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search_player']
    def get_players(self):
        return Player.objects.filter(last_name__icontains=self.search)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['forms'] = self.form
        context['player'] = self.player
        # context['qs_json'] = json.dumps(list(Player.objects.values()))
        context['qs_json'] = json.dumps(list(Player.objects.values()))
        if self.search:
            context['query'] = urlencode({'search_player': self.search})
            context['search_player'] = self.search
        return context

    def get_success_url(self):
        return reverse('webapp:index')


