from captcha.fields import CaptchaField
from phonenumber_field.formfields import PhoneNumberField
from django import forms
from django.forms import FileInput, widgets
from webapp.models import File, CLASS_CHOICES, Calendar, News, Player, Club, Tournament, Participant, Recommendation, \
    Partner
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime
import re

latin_regex = re.compile(r'^[a-zA-Z\- ]+$')


def validate_latin_chars(value):
    if not latin_regex.match(value):
        raise ValidationError(
            _('Введите только латинские буквы.'),
            params={'value': value},
        )


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']
        widgets = {'file': FileInput(attrs={'accept': 'application/xml'})}


class PlayerSearchForm(forms.Form):
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
        fields = ['event_name', 'event_city', 'event_date', 'text', 'deadline']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'deadline': forms.DateTimeInput(attrs={'type': 'date'})
        }


class CalendarBulkDeleteForm(forms.Form):
    checkboxes = forms.ModelMultipleChoiceField(Calendar.objects.all(), widget=forms.CheckboxSelectMultiple)


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

    def clean_search_date(self):
        search_date = self.cleaned_data['search_date']
        if search_date is not None:
            date_str = str(search_date)
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                raise ValidationError(
                    "Дата турнира была некорректно введена! Введите дату турнира в корректном формате.")
        return search_date


class CompetitorSearchForm(forms.Form):
    search_rank = forms.CharField(required=True, label='Найти',
                                  widget=widgets.TextInput(
                                      attrs={'class': "form-control w-30", 'placeholder': 'Ранк'}))
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


class NewsBulkDeleteForm(forms.Form):
    checkboxes = forms.ModelMultipleChoiceField(News.objects.all(), widget=forms.CheckboxSelectMultiple)


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', "last_name", 'birth_date', 'avatar']
        widgets = {
            'birth_date': widgets.DateInput(attrs={'type': 'date'})}


class ClubSearch(forms.Form):
    search_name = forms.CharField(max_length=50, required=False, label='Найти',
                                  widget=widgets.TextInput(
                                      attrs={'class': "form-control w-30", 'placeholder': 'Имя клуба'}))
    search_city = forms.CharField(max_length=50, required=False, label='Найти',
                                  widget=widgets.TextInput(
                                      attrs={'class': "form-control w-30", 'placeholder': 'Город'}))


class CheckPlayerForm(forms.Form):
    Surname = forms.CharField(max_length=255)
    FirstName = forms.CharField(max_length=255)
    EgdPin = forms.IntegerField()
    Rating = forms.FloatField()
    GoLevel = forms.CharField(max_length=255)
    birth_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    id_in_game = forms.IntegerField()

    def clean_Surname(self):
        Surname = self.cleaned_data.get('Surname')
        return Surname

    def clean_FirstName(self):
        FirstName = self.cleaned_data.get('FirstName')
        return FirstName

    def clean_EgdPin(self):
        EgdPin = self.cleaned_data.get('EgdPin')
        return EgdPin

    def clean_Rating(self):
        Rating = self.cleaned_data.get('Rating')
        return Rating

    def clean_GoLevel(self):
        GoLevel = self.cleaned_data.get("GoLevel")
        return GoLevel

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > timezone.now().date():
            raise forms.ValidationError('Поле даты рождения была некорректна заполнена! Отредактируйте данное поле.')
        return birth_date


class CheckTournamentForm(forms.Form):
    Name = forms.CharField(max_length=255)
    location = forms.CharField(max_length=255)
    Boardsize = forms.IntegerField()
    NumberOfRounds = forms.IntegerField()
    regulations = forms.CharField(max_length=255)
    date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    city = forms.CharField(max_length=255)
    tournament_class = forms.ChoiceField(choices=CLASS_CHOICES)

    def clean_Name(self):
        Name = self.cleaned_data.get('Name')
        return Name

    def clean_location(self):
        location = self.cleaned_data.get('location')
        return location

    def clean_tournament_class(self):
        tournament_class = self.cleaned_data.get('tournament_class')
        return tournament_class

    def clean_city(self):
        city = self.cleaned_data.get('city')
        return city

    def clean_Boardsize(self):
        Boardsize = self.cleaned_data.get('Boardsize')
        return Boardsize

    def clean_regulations(self):
        regulations = self.cleaned_data.get('regulations')
        return regulations

    def clean_NumberOfRounds(self):
        NumberOfRounds = self.cleaned_data.get('NumberOfRounds')
        return NumberOfRounds

    def clean_date(self):
        date = self.cleaned_data.get('date')
        return date


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['logo', 'name', 'EGDName', 'num_players', 'city', 'coaches', 'address', 'phonenumber', 'web_link',
                  'schedule']
        widgets = {
            'coaches': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'logo': 'Logo:',
            'name': 'Club name:',
            'EGDName': 'EGD name:',
            'city': 'City:',
            'coaches': 'Coaches:',
            'num_players': 'Number of members:',
            'address': "Address",
            'phonenumber': "Phone number",
            'web_link': "Link to social media or web-site",
            'schedule': 'Working hours',
        }

    def clean_num_players(self):
        num_players = self.cleaned_data.get('num_players')
        active_players_count = self.instance.players.count()
        if active_players_count and num_players:
            if num_players < active_players_count:
                raise ValidationError(
                    'Number of members cannot be less than the number of active players!')
            return num_players
        else:
            return num_players


class ClubCreateForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['logo', 'name', 'EGDName', 'num_players', 'city', 'coaches', 'address', 'phonenumber', 'web_link',
                  'schedule']
        widgets = {
            'coaches': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'logo': 'Логотип:',
            'name': 'Название:',
            'EGDName': 'EGD name:',
            'city': 'Город:',
            'coaches': 'Тренеры:',
            'num_players': 'Количество участников:',
            'address': "Адрес",
            'phonenumber': "Номер телефона",
            'web_link': "Ссылка на соц. сети или сайт",
            'schedule': 'Рабочие часы',
        }


class ParticipantForm(forms.ModelForm):
    name = forms.CharField(validators=[validate_latin_chars], label='',
                           widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
                               "First name", "id": "id_name", 'style': "width:200px"}))
    surname = forms.CharField(validators=[validate_latin_chars], label='',
                              widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
                                  "Last name", "id": "id_surname", 'style': "width:200px"}))
    rank = forms.CharField(label='', widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
        "Rank", "id": "id_rank", 'style': "width:200px"}))
    city = forms.CharField(required=False, validators=[validate_latin_chars], label='',
                              widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
                                  "City", "id": "id_city", 'style': "width:200px"}))
    phonenumber = forms.CharField(label='', widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
        "Phone number", "id": "id_phonenumber", 'style': "width:200px"}))

    class Meta:
        model = Participant
        fields = ['surname', 'name', 'rank', 'city', 'phonenumber']

    def clean_name(self):
        return re.sub(' +', ' ', self.cleaned_data['name'].strip().capitalize())

    def clean_surname(self):
        return re.sub(' +', ' ', self.cleaned_data['surname'].strip().capitalize())

    def clean_rank(self):
        return self.cleaned_data['rank'].strip().lower()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.name = re.sub(' +', ' ', self.cleaned_data['name'].strip().capitalize())
        instance.surname = re.sub(' +', ' ', self.cleaned_data['surname'].strip().capitalize())
        instance.rank = self.cleaned_data['rank'].strip().lower()
        if commit:
            instance.save()
        return instance


class SearchParPlayer(forms.Form):
    search_player = forms.CharField(required=False,
                                    widget=widgets.TextInput(
                                        attrs={'class': "form-control", 'placeholder': "Enter only last name",
                                               'id': "search_last_name", 'style': "width: 400px", 'type': "hidden"}))


class RecommendationForm(forms.ModelForm):
    class Meta:
        model = Recommendation
        fields = ['text']


class FeedbackToEmailForm(forms.Form):
    first_name = forms.CharField(required=True, max_length=50, widget=widgets.TextInput(
        attrs={'class': "form-control", 'placeholder': "Ваше имя", 'name': "first_name"}))
    last_name = forms.CharField(required=True, max_length=50, widget=widgets.TextInput(
        attrs={'class': "form-control", 'placeholder': "Ваша фамилия", 'name': "last_name"}))
    phone_number = forms.CharField(required=False, max_length=50, widget=widgets.TextInput(
        attrs={'class': "form-control", 'placeholder': "Ваш номер телефона", 'name': "phone_number"}))
    email = forms.EmailField(required=True, max_length=150, widget=widgets.EmailInput(
        attrs={'class': "form-control", 'placeholder': "ваш e-mail", 'name': "email"}))
    message = forms.CharField(required=True, widget=widgets.Textarea(
        attrs={'class': "form-control", 'placeholder': "ваше предложение или замечание", 'name': "message"}),
                              max_length=3000)
    captcha = CaptchaField()


class EmailToChangeRegInfoFrom(FeedbackToEmailForm):
    phone_number = PhoneNumberField(required=True, region='KG', widget=widgets.TextInput(
        attrs={'class': "form-control", 'placeholder': "Ваш номер телефона", 'name': "phone_number"}))
    message = forms.CharField(required=True, widget=widgets.Textarea(
        attrs={'class': "form-control", 'placeholder': "В чем была ошибка? И как надо исправить?", 'name': "message"}),
                              max_length=3000)


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ['name', 'logo', 'web_link']
