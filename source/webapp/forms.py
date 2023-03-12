from django import forms
from django.forms import FileInput, widgets
from webapp.models import File, CLASS_CHOICES, Calendar, News, Player, Club, Tournament


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


class CalendarForm(forms.ModelForm):
    class Meta:
        model = Calendar
        fields = ['event_name', 'event_city', 'event_date']
        widgets = {'event_date': forms.DateInput(attrs={'type': 'date'})}


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


class CompetitorSearchForm(forms.Form):
    search_rank = forms.IntegerField(required=True, min_value=0, label='Найти',
                                  widget=widgets.TextInput(
                                      attrs={'class': "form-control w-30", 'placeholder': 'Ранк'}))
    search_age = forms.IntegerField(required=True, label='Найти',
                                    widget=widgets.NumberInput(
                                        attrs={'class': "form-control w-30", 'placeholder': 'Возраст'}))
    search_clubs = forms.CharField(max_length=50, required=False, label='Найти',
                                   widget=widgets.TextInput(
                                       attrs={'class': "form-control w-30", 'placeholder': 'Клуб'}))
    search_city = forms.CharField(max_length=50, required=False, label='Найти',
                                  widget=widgets.TextInput(
                                      attrs={'class': "form-control w-30", 'placeholder': 'Город'}))
    search_country = forms.CharField(max_length=50, required=False, label='Найти',
                                     widget=widgets.TextInput(
                                         attrs={'class': "form-control w-30", 'placeholder': 'Страна'}))


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'text', 'news_image']
        widgets = {
            'text': widgets.Textarea(attrs={"cols": 24, "rows": 3, 'class': 'form-control', 'placeholder': 'Текст'}),
            'title': widgets.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок'})}


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', "last_name", 'patronymic', 'birth_date', 'avatar']
        widgets = {
            'birth_date': widgets.DateInput(attrs={'type': 'date'})}

class ClubSearch(forms.Form):
    search_name = forms.CharField(max_length=50, required=False, label='Найти',
                                        widget=widgets.TextInput(
                                            attrs={'class': "form-control w-30", 'placeholder': 'Имя клуба'}))
    search_city = forms.CharField(max_length=50, required=False, label='Найти',
                                  widget=widgets.TextInput(
                                      attrs={'class': "form-control w-30", 'placeholder': 'Город'}))

class CheckPlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['patronymic', 'birth_date']
        widgets = {'birth_date': DateInput(attrs={'type': 'date'})}


class CheckTournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['date', 'city']
        widgets = {'date': DateInput(attrs={'type': 'date'})}
