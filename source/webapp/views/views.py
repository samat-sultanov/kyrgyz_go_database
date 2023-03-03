from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from webapp.handle_upload import handle_uploaded_file
from webapp.models import File, News , Calendar
from webapp.forms import FileForm
from django.views.generic import ListView

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar = Calendar.objects.order_by('event_date')
        context['calendar'] = calendar
        return context

# Create your views here.

def file_upload(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            a = form.save()
            handle_uploaded_file(request.FILES['file'])
            file = get_object_or_404(File, pk=a.id)
            file.delete()
        else:
            return render(request, 'file_upload.html', {'form': form})
        return HttpResponseRedirect("/")
    else:
        form = FileForm
    return render(request, 'file_upload.html', {'form': form})


class NewsListView(ListView):
    model = News
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    ordering = ['-created_at']
