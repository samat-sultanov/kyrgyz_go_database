from django.shortcuts import get_object_or_404

from webapp.models import Calendar
from webapp.forms import CalendarForm
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView


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
    model = Calendar

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('webapp:index')
