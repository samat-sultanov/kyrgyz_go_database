from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from webapp.forms import CarouselForm
from webapp.models import Carousel


class CarouselCreateView(LoginRequiredMixin, CreateView):
    model = Carousel
    form_class = CarouselForm
    template_name = 'carousel/carousel_create.html'

    def get_success_url(self):
        return reverse('webapp:index')


class CarouselUpdateView(LoginRequiredMixin, UpdateView):
    model = Carousel
    template_name = 'carousel/carousel_update.html'
    form_class = CarouselForm

    def get_success_url(self):
        return reverse('webapp:index')


class CarouselDeleteView(LoginRequiredMixin, DeleteView):
    model = Carousel
    success_url = reverse_lazy('webapp:index')
