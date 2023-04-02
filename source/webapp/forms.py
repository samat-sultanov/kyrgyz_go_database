from captcha.fields import CaptchaField
from phonenumber_field.formfields import PhoneNumberField
from django import forms
from django.forms import FileInput, widgets
from webapp.models import File, CLASS_CHOICES, Calendar, News, Player, Club, Tournament, Participant, Recommendation, Partner
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_latin_chars(value):
    if not value.isascii() or not value.isalpha():
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


class CheckPlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['birth_date']
        widgets = {'birth_date': DateInput(attrs={'type': 'date'})}


class CheckTournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['date', 'city', 'tournament_class', 'regulations', 'uploaded_by']
        widgets = {'date': DateInput(attrs={'type': 'date'})}


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


class ParticipantForm(forms.ModelForm):
    name = forms.CharField(validators=[validate_latin_chars], label='', widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
        "First name", "id": "id_name", 'style': "width:200px"}))
    surname = forms.CharField(validators=[validate_latin_chars], label='', widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
        "Last name", "id": "id_surname", 'style': "width:200px"}))
    rank = forms.CharField(label='', widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
        "Rank", "id": "id_rank", 'style': "width:200px"}))
    phonenumber = forms.CharField(label='', widget=forms.TextInput(attrs={'class': "form-control", 'placeholder':
        "Phone number", "id": "id_phonenumber", 'style': "width:200px"}))

    class Meta:
        model = Participant
        fields = ['surname', 'name', 'rank', 'phonenumber']


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