from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, CreateView

from webapp.models import News
from webapp.forms import NewsForm


# Этот класс написан Акрамом. Я - Дастан, перенес его в этот файл из views.py
class NewsListView(ListView):
    model = News
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    ordering = ['-created_at']


class NewsCreateView(LoginRequiredMixin, CreateView):
    model = News
    form_class = NewsForm
    template_name = 'news/news_create.html'
    context_object_name = 'news'

    # Когда будет готово представление и шаблон детального просмотра статьи, надо будет success_url поменять
    def get_success_url(self):
        return reverse('webapp:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
