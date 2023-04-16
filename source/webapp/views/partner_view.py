from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from webapp.models import Partner
from webapp.forms import PartnerForm
from django.contrib.auth.mixins import PermissionRequiredMixin


class PartnersListView(ListView):
    model = Partner
    template_name = 'partner/partners_list.html'
    context_object_name = 'partners_list'


class PartnerCreateView(PermissionRequiredMixin, CreateView):
    model = Partner
    form_class = PartnerForm
    template_name = 'partner/partner_create.html'
    permission_required = ('webapp.add_partner',)

    def get_success_url(self):
        return reverse('webapp:partner_detail', kwargs={'pk': self.object.pk})


class PartnerDetailView(PermissionRequiredMixin, DetailView):
    model = Partner
    template_name = 'partner/partner_detail.html'
    context_object_name = 'partner'
    permission_required = ('webapp.partner_detail',)


class PartnerUpdateView(PermissionRequiredMixin, UpdateView):
    model = Partner
    template_name = 'partner/partner_update.html'
    form_class = PartnerForm
    context_object_name = 'partner'
    permission_required = ('webapp.change_partner',)

    def get_success_url(self):
        return reverse('webapp:partner_detail', kwargs={'pk': self.object.pk})


class PartnerDeleteView(PermissionRequiredMixin, DeleteView):
    model = Partner
    success_url = reverse_lazy('webapp:partners_list')
    template_name = 'partner/partner_delete.html'
    permission_required = ('webapp.delete_partner',)
