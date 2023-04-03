import json
from datetime import datetime

from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from webapp.models import Calendar, Participant, Player
from webapp.forms import CalendarForm, CalendarBulkDeleteForm, ParticipantForm, SearchParPlayer, \
    EmailToChangeRegInfoFrom
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView, FormView, DetailView, View


class CalendarDetailView(TemplateView):
    template_name = 'calendar/calendar_view.html'

    def get_context_data(self, **kwargs):
        pk = kwargs.get('pk')
        event = get_object_or_404(Calendar, pk=pk)
        kwargs['event'] = event
        return super().get_context_data(**kwargs)


class CalendarCreateView(LoginRequiredMixin, CreateView):
    template_name = 'calendar/calendar_create.html'
    model = Calendar
    form_class = CalendarForm

    def get_success_url(self):
        return reverse('webapp:index')


class CalendarUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'calendar/calendar_update.html'
    model = Calendar
    form_class = CalendarForm

    def get_success_url(self):
        return reverse('webapp:index')


class CalendarDeleteView(PermissionRequiredMixin, DeleteView):
    queryset = Calendar.objects.all().filter(is_deleted=False)
    context_object_name = 'event'
    success_url = reverse_lazy('webapp:index')
    permission_required = ('webapp.delete_calendar',)

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.is_deleted = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class DeletedCalendarListView(PermissionRequiredMixin, FormView):
    form_class = CalendarBulkDeleteForm
    template_name = 'calendar/calendar_deleted_list.html'
    permission_required = ('webapp.view_deleted_events',)

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

    def form_valid(self, form):
        event = get_object_or_404(Calendar, pk=self.kwargs.get('pk'))
        surname = self.request.POST.get('surname')
        name = self.request.POST.get('name')
        phonenumber = self.request.POST.get('phonenumber')
        participants = event.participant.all()
        for participant in participants:
            if name == participant.name and surname == participant.surname:
                form.add_error('name', 'Данный игрок уже зарегистрирован.')
                return super().form_invalid(form)
            elif phonenumber == participant.phonenumber:
                form.add_error('phonenumber', 'Номер телефона уже зарегистрирован.')
                return super().form_invalid(form)
        form.instance.event = event
        return super().form_valid(form)

    def get_search_form(self):
        return SearchParPlayer(self.request.GET)

    def get(self, request, *args, **kwargs):
        event = get_object_or_404(Calendar, pk=self.kwargs.get('pk'))
        if datetime.now().date() > event.deadline:
            return redirect(reverse('webapp:index'))
        self.forms = self.get_search_form()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['forms'] = self.get_search_form()
        return context

    def get_success_url(self):
        return reverse('webapp:event_view', kwargs={'pk': self.object.event.pk})


def calendar_player_list(request, *args, **kwargs):
    event = get_object_or_404(Calendar, pk=kwargs.get('pk'))

    if request.method == 'GET':
        form = EmailToChangeRegInfoFrom()
        context = {'event': event, 'form': form}
        return render(request, 'calendar/player_list_e.html', context)

    elif request.method == "POST":
        form = EmailToChangeRegInfoFrom(request.POST)
        if form.is_valid():
            human = True
            subject = f"Допустил ошибку при регистрации на ивент/турнир c ID '{kwargs.get('pk')}'"
            body = {
                'tournament/event': f"Ивент/Турнир: [{kwargs.get('pk')}] {Calendar.objects.all().get(pk=kwargs.get('pk')).event_name}",
                'first_name': f"Имя: {form.cleaned_data.get('first_name', None)}",
                'last_name': f"Фамилия: {form.cleaned_data.get('last_name', None)}",
                'email': f"почта: {form.cleaned_data.get('email', None)}",
                'phone_number': f"номер телефона: {form.cleaned_data.get('phone_number', None)}",
                'message': f"Запрос: ''{form.cleaned_data.get('message')}''",
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
            return redirect("webapp:CalendarPlayerList", pk=kwargs.get('pk'))
        else:
            form = EmailToChangeRegInfoFrom(request.POST)
            context = {'event': event, 'form': form, 'offcanvas': 'off'}
            return render(request, 'calendar/player_list_e.html', context)


class StatusChange(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        part = get_object_or_404(Participant, pk=self.kwargs.get('pk'))
        status_res = None
        if part.status == 'Confirmed':
            part.status = 'Not confirmed'
            part.save()
            status_res = True
        else:
            part.status = 'Confirmed'
            part.save()
            status_res = False
        response = JsonResponse({'status_res': status_res})
        return response


class DeletePlayerFromEvent(LoginRequiredMixin, DeleteView):
    model = Participant

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def get_success_url(self):
        return reverse('webapp:CalendarPlayerList', kwargs={'pk': self.object.event.pk})