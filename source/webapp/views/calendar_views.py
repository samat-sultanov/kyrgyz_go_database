from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from webapp.models import Calendar
from webapp.forms import CalendarForm
from django.urls import reverse, reverse_lazy
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
    queryset = Calendar.objects.all().filter(is_deleted=False)
    context_object_name = 'event'
    success_url = reverse_lazy('webapp:index')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.is_deleted = True
        self.object.save()
        return HttpResponseRedirect(success_url)
