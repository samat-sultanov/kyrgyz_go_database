from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from webapp.handle_upload import handle_uploaded_file
from webapp.models import File
from webapp.forms import FileForm
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class IndexView(TemplateView):
    template_name = 'index.html'

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
    return render(request, 'file_upload.html', {'form':form})