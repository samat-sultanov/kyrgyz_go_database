from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from webapp.models import Calendar
from webapp.forms import CalendarForm, CalendarBulkDeleteForm
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView, FormView


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


class DeletedNewsListView(FormView):
    form_class = CalendarBulkDeleteForm
    template_name = 'calendar/calendar_deleted_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deleted_calendar_list'] = Calendar.objects.all().filter(is_deleted=True).order_by('updated_at')
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['checkboxes'].queryset = News.objects.all().filter(is_deleted=True).order_by('updated_at')
        return form

    def form_valid(self, form):
        selected_to_delete = News.objects.filter(pk__in=list(map(int, self.request.POST.getlist('checkboxes'))))
        print(selected_to_delete)
        selected_to_delete.delete()
        return HttpResponseRedirect(reverse_lazy('webapp:deleted_news_list'))
