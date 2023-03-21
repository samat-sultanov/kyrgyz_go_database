from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, FormView

from webapp.models import News
from webapp.forms import NewsForm, NewsBulkDeleteForm


# Этот класс написан Акрамом(Данияром). Я - Дастан, перенес его в этот файл из views.py
class NewsListView(ListView):
    queryset = News.objects.all().filter(is_deleted=False).order_by('-created_at')
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'


class NewsCreateView(LoginRequiredMixin, CreateView):
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
    queryset = News.objects.all().filter(is_deleted=False)
    context_object_name = 'single_news'
    success_url = reverse_lazy('webapp:news_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.is_deleted = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class DeletedNewsListView(FormView):
    form_class = NewsBulkDeleteForm
    template_name = 'news/news_deleted_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deleted_news_list'] = News.objects.all().filter(is_deleted=True).order_by('updated_at')
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


def restore_one_deleted_news(request, *args, **kwargs):
    if request.method == 'GET':
        news = get_object_or_404(News, pk=kwargs.get('pk'))
        news.is_deleted = False
        news.save()
        return redirect('webapp:deleted_news_list')


def hard_delete_one_news(request, *args, **kwargs):
    if request.method == 'POST':
        news = get_object_or_404(News, pk=kwargs.get('pk'))
        news.delete()
        return redirect('webapp:deleted_news_list')
