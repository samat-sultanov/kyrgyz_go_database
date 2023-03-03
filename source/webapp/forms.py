from django import forms
from django.forms import FileInput, widgets
from webapp.models import File


class FileForm(forms.ModelForm):
   class Meta:
      model = File
      fields = ['file']
      widgets = {'file': FileInput(attrs={'accept': 'application/xml'})}

class PlayerSearchForm(forms.Form):
   search_patronymic = forms.CharField(max_length=50, required=False, label='Найти',
                                  widget=widgets.TextInput(
                                      attrs={'class': "form-control w-30", 'placeholder': 'Отчество'}))
   search_first_name = forms.CharField(max_length=50, required=False, label='Найти',
                                  widget=widgets.TextInput(
                                     attrs={'class': "form-control w-30", 'placeholder': 'Имя'}))
   search_last_name = forms.CharField(max_length=50, required=False, label='Найти',
                                 widget=widgets.TextInput(attrs={'class': "form-control w-30", 'placeholder': 'Фамилия'}))
   search_clubs = forms.CharField(max_length=50, required=False, label='Найти',
                                 widget=widgets.TextInput(attrs={'class': "form-control w-30", 'placeholder': 'Клуб'}))
   search_city = forms.CharField(max_length=50, required=False, label='Найти',
                                  widget=widgets.TextInput(attrs={'class': "form-control w-30", 'placeholder': 'Город'}))

