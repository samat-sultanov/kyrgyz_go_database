from django.urls import reverse
from django.views.generic import CreateView
from webapp.models import Partner
from webapp.forms import PartnerForm


class PartnerCreateView(CreateView):
    model = Partner
    form_class = PartnerForm
    template_name = 'partner/partner_create.html'

    def get_success_url(self):
        return reverse('accounts:detail', kwargs={'pk': self.request.user.pk})
