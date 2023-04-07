from django.urls import reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from webapp.models import Partner
from webapp.forms import PartnerForm


class PartnersListView(ListView):
    model = Partner
    template_name = 'partner/partners_list.html'
    context_object_name = 'partners_list'


class PartnerCreateView(CreateView):
    model = Partner
    form_class = PartnerForm
    template_name = 'partner/partner_create.html'

    def get_success_url(self):
        return reverse('webapp:partner_detail', kwargs={'pk': self.object.pk})


class PartnerDetailView(DetailView):
    model = Partner
    template_name = 'partner/partner_detail.html'
    context_object_name = 'partner'


class PartnerUpdateView(UpdateView):
    model = Partner
    template_name = 'partner/partner_update.html'
    form_class = PartnerForm
    context_object_name = 'partner'

    def get_success_url(self):
        return reverse('webapp:partner_detail', kwargs={'pk': self.object.pk})
