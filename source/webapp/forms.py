from django import forms
from django.forms import FileInput, widgets
from webapp.models import File, CLASS_CHOICES


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
                                       widget=widgets.TextInput(
                                           attrs={'class': "form-control w-30", 'placeholder': 'Фамилия'}))
    search_clubs = forms.CharField(max_length=50, required=False, label='Найти',
                                   widget=widgets.TextInput(
                                       attrs={'class': "form-control w-30", 'placeholder': 'Клуб'}))
    search_city = forms.CharField(max_length=50, required=False, label='Найти',
                                  widget=widgets.TextInput(
                                      attrs={'class': "form-control w-30", 'placeholder': 'Город'}))


class DateInput(forms.DateInput):
    input_type = 'date'


class TournamentSearchForm(forms.Form):
    search_name = forms.CharField(max_length=50, required=False, label='Найти',
                                  widget=widgets.TextInput(
                                      attrs={'class': "form-control w-30", 'placeholder': 'Название'}))
    search_city = forms.CharField(max_length=50, required=False, label='Найти',
                                  widget=widgets.TextInput(
                                      attrs={'class': "form-control w-30", 'placeholder': 'Город'}))
    search_date = forms.DateField(required=False, label='Найти',
                                  widget=DateInput(attrs={'class': "form-control w-30"}))
    search_tournament_class = forms.CharField(required=False, widget=forms.Select(choices=CLASS_CHOICES,
                                                                                  attrs={'class': "form-control w-30"}))
