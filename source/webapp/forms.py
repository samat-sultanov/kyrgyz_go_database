from django import forms
from django.forms import FileInput
from .models import File


class FileForm(forms.ModelForm):
   class Meta:
      model = File
      fields = ['file']
      widgets = {'file': FileInput(attrs={'accept': 'application/xml'})}

