from django.views.generic import ListView

from webapp.models import News


# Этот класс написан Акрамом. Я - Дастан, перенес его в этот файл из views.py
class NewsListView(ListView):
    model = News
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    ordering = ['-created_at']
