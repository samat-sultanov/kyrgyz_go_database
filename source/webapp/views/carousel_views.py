from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView
from webapp.forms import CarouselForm
from webapp.models import Carousel


class CarouselCreateView(LoginRequiredMixin, CreateView):
    model = Carousel
    form_class = CarouselForm
    template_name = 'carousel/carousel_create.html'

    def get_success_url(self):
        return reverse('webapp:index')