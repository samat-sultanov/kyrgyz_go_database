from captcha.fields import CaptchaField
from phonenumber_field.formfields import PhoneNumberField
import re
import requests

from django import forms
from django.forms import FileInput, widgets
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from webapp.models import File, CLASS_CHOICES, Calendar, News, Player, Club, Tournament, Participant, Recommendation, \
    Partner, DEFAULT_CLASS, DayOfWeek, Country


latin_regex = re.compile('^[a-zA-Z_.,\\- ]+$')


def get_countries():
    base_url = 'https://restcountries.com/v3.1/alpha/'
    list_of_countries = [("", "  -----  "), ('kg', 'Кыргызстан'), ('uz', 'Узбекистан'), ('kz', 'Казахстан')]
    countries = []
    for player in Player.objects.all():
        if player.country not in countries:
            countries.append(player.country)
    for country in countries:
        raw_response = requests.get(base_url + country.country_code)
        if raw_response.status_code == 200:
            response = raw_response.json()
            for element in response:
                for k, v in element.items():
                    if k == "translations":
                        try:
                            rus_names = v.get("rus")
                            name_to_append = rus_names.get("common")
                            if name_to_append:
                                if name_to_append == 'Киргизия':
                                    name_to_append = 'Кыргызстан'
                                to_append = (country.country_code, name_to_append)
                                if to_append not in list_of_countries:
                                    list_of_countries.append(to_append)
                            else:
                                to_append = (country.country_code, rus_names.get("official"))
                                if to_append not in list_of_countries:
                                    list_of_countries.append(to_append)
                        except ObjectDoesNotExist:
                            common = response[0].get("common")
                            to_append = (country.country_code, common)
                            if to_append not in list_of_countries:
                                list_of_countries.append(to_append)
        else:
            continue
    return list_of_countries


COUNTRIES = get_countries()


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
        fields = ['event_name', 'event_city', 'event_date', 'text', 'deadline', 'calendar_image']
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
                                      attrs={'class': "form-control w-30", 'placeholder': 'Ранг'}))
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
        fields = ['title', 'text', 'news_image', 'video_link']
        widgets = {
            'text': widgets.Textarea(attrs={"cols": 24, "rows": 3, 'class': 'form-control', 'placeholder': 'Текст'}),
            'title': widgets.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заголовок'})}

    def clean(self):
        cleaned_data = super().clean()
        video_link = cleaned_data.get('video_link')
        news_image = cleaned_data.get('news_image')

        if video_link and news_image:
            raise forms.ValidationError('Вы можете заполнить только одно из полей "Видео" или "Картинка".')

        return cleaned_data


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
    position = forms.CharField(widget=forms.widgets.TextInput(attrs={'style': 'width: 100px;'}))
    results = forms.CharField(widget=forms.widgets.TextInput(attrs={'disabled': 'disabled'}))
    Surname = forms.CharField(max_length=255, widget=forms.widgets.TextInput(attrs={'style': 'width: 150px;'}))
    FirstName = forms.CharField(max_length=255, widget=forms.widgets.TextInput(attrs={'style': 'width: 150px;'}))
    EgdPin = forms.IntegerField(widget=forms.widgets.TextInput(attrs={'style': 'width: 150px;'}))
    Club = forms.CharField(max_length=255, widget=forms.widgets.TextInput(attrs={'style': 'width: 150px;'}))
    Rating = forms.IntegerField(widget=forms.widgets.TextInput(attrs={'style': 'width: 100px;', 'maxlength': '4'}))
    GoLevel = forms.CharField(max_length=3, widget=forms.widgets.TextInput(attrs={'style': 'width: 100px;'}))
    birth_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=False)
    id_in_tournament = forms.IntegerField(widget=forms.widgets.TextInput(attrs={'disabled': 'disabled'}))

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > timezone.now().date():
            raise forms.ValidationError('Поле даты рождения была некорректна заполнена! Отредактируйте данное поле.')
        return birth_date

    def clean_rating(self):
        rating = self.cleaned_data.get('Rating')
        if rating > 4:
            raise forms.ValidationError('Рейтинг должен быть до 4')
        return rating


class CheckTournamentForm(forms.Form):
    Name = forms.CharField(max_length=255)
    location = forms.CharField(max_length=255, required=False)
    Boardsize = forms.IntegerField()
    NumberOfRounds = forms.IntegerField()
    regulations = forms.CharField(max_length=255, required=False)
    date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), required=True)
    country = forms.ChoiceField(choices=COUNTRIES, required=True)
    region = forms.CharField(max_length=100, required=False)
    city = forms.CharField(max_length=255, required=False)
    tournament_class = forms.ChoiceField(choices=CLASS_CHOICES, required=True)

    def clean_tournament_class(self):
        tournament_class = self.cleaned_data.get('tournament_class')
        if tournament_class == DEFAULT_CLASS:
            self.add_error('tournament_class', 'Выберите корректный класс турнира!')
        return tournament_class

    def clean_country(self):
        country = self.cleaned_data.get('country')
        if country == '':
            self.add_error('country', 'Выберите страну проведения турнира!')
        return country


class ClubForm(forms.ModelForm):
    day_of_week = forms.ModelMultipleChoiceField(queryset=DayOfWeek.objects.all(), required=False,label='Выходные', widget=forms.CheckboxSelectMultiple())
    days_of_work = forms.ModelMultipleChoiceField(queryset=DayOfWeek.objects.all(), required=False,label='Рабочие дни', widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = Club
        fields = ['logo', 'name', 'EGDName', 'num_players', 'city', 'coaches', 'address', 'phonenumber', 'web_link',
                  'schedule_from', 'schedule_to', 'breakfast_from', 'breakfast_to', 'days_of_work', 'day_of_week']
        widgets = {
            'coaches': forms.CheckboxSelectMultiple(),
            'schedule_from': forms.TextInput(attrs={'type': 'time', 'step': '60'}),
            'schedule_to': forms.TextInput(attrs={'type': 'time', 'step': '60'}),
            'breakfast_from': forms.TextInput(attrs={'type': 'time', 'step': '60'}),
            'breakfast_to': forms.TextInput(attrs={'type': 'time', 'step': '60'}),
        }
        labels = {
            'logo': 'Логотип:',
            'name': 'Наименование клуба:',
            'EGDName': 'EGD name:',
            'city': 'Город:',
            'coaches': 'Тренера:',
            'num_players': 'Число участников:',
            'address': "Адрес:",
            'phonenumber': "Номер телефона:",
            'web_link': "Web-site:",
            'schedule_from': "Работаем С",
            'schedule_to': "До",
            'breakfast_from': "Обед с",
            'breakfast_to': "До",
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
    day_of_week = forms.ModelMultipleChoiceField(queryset=DayOfWeek.objects.all(), required=False,label='Выходные', widget=forms.CheckboxSelectMultiple())
    days_of_work = forms.ModelMultipleChoiceField(queryset=DayOfWeek.objects.all(), required=False,label='Рабочие дни', widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = Club
        fields = ['logo', 'name', 'EGDName', 'num_players', 'city', 'coaches', 'address', 'phonenumber', 'web_link',
                  'schedule_from', 'schedule_to', 'breakfast_from', 'breakfast_to', 'days_of_work', 'day_of_week']
        widgets = {
            'coaches': forms.CheckboxSelectMultiple(),
            'schedule_from': forms.TextInput(attrs={'type': 'time', 'step': '60'}),
            'schedule_to': forms.TextInput(attrs={'type': 'time', 'step': '60'}),
            'breakfast_from': forms.TextInput(attrs={'type': 'time', 'step': '60'}),
            'breakfast_to': forms.TextInput(attrs={'type': 'time', 'step': '60'}),
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
            'schedule_from': "Работаем С",
            'schedule_to': "До",
            'breakfast_from': "Обед с",
            'breakfast_to': "До",
        }


class ParticipantForm(forms.ModelForm):
    name = forms.CharField(validators=[validate_latin_chars], label='Имя',
                           widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
                               "First name", "id": "id_name", 'style': "width:200px"}))
    surname = forms.CharField(validators=[validate_latin_chars], label='Фамилия',
                              widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
                                  "Last name", "id": "id_surname", 'style': "width:200px"}))
    rank = forms.CharField(label='Ранг', widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
        "Rank", "id": "id_rank", 'style': "width:200px"}))
    city = forms.CharField(required=False, validators=[validate_latin_chars], label='Город',
                              widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
                                  "City", "id": "id_city", 'style': "width:200px"}))
    phonenumber = forms.CharField(label='Номер телефона', widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
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

class CalendarUpdateForm(forms.ModelForm):
    event_date = forms.DateField(required=False, widget=widgets.TextInput(
        attrs={'type': "date"}))
    deadline = forms.DateField(required=False, widget=widgets.TextInput(
        attrs={'type': "date"}))
    class Meta:
        model = Calendar
        fields = ['event_name', 'event_city', 'event_date', 'text', 'deadline', 'calendar_image']
