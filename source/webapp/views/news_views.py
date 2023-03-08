from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from webapp.models import News
from webapp.forms import NewsForm


# Этот класс написан Акрамом(Данияром). Я - Дастан, перенес его в этот файл из views.py
class NewsListView(ListView):
    queryset = News.objects.all().filter(is_deleted=False).order_by('-created_at')
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'


class NewsCreateView(CreateView):  # добавить LoginRequiredMixin, когда будет реализована аутентификация
    model = News
    form_class = NewsForm
    template_name = 'news/news_create.html'
    context_object_name = 'news'

    def get_success_url(self):
        return reverse('webapp:news_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class NewsDetailView(DetailView):
    queryset = News.objects.all().filter(is_deleted=False)
    template_name = 'news/news_detail.html'
    context_object_name = 'single_news'


class NewsUpdateView(UpdateView):
    model = News
    template_name = 'news/news_update.html'
    form_class = NewsForm
    context_object_name = 'single_news'
    queryset = News.objects.all().filter(is_deleted=False)

    def get_success_url(self):
        return reverse('webapp:news_detail', kwargs={'pk': self.object.pk})


class NewsDeleteView(DeleteView):
    model = News
    context_object_name = 'single_news'
    success_url = reverse_lazy('webapp:news_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.is_deleted = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class DeletedNewsListPage(ListView):
    queryset = News.objects.all().filter(is_deleted=True)
    context_object_name = 'deleted_news_list'
    template_name = 'news/news_deleted_list.html'
