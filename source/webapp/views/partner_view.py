from django.urls import reverse
from django.views.generic import CreateView, ListView
from webapp.models import Partner
from webapp.forms import PartnerForm


class PartnersListView(ListView):
    queryset = Partner.objects.all()
    template_name = 'partner/partners_list.html'
    context_object_name = 'partners_list'


class PartnerCreateView(CreateView):
    model = Partner
    form_class = PartnerForm
    template_name = 'partner/partner_create.html'

    def get_success_url(self):
        return reverse('accounts:detail', kwargs={'pk': self.request.user.pk})
