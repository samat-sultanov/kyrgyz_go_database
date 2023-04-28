from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import EmailField, BooleanField
from django import forms

from webapp.models import Country

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = EmailField(
        label="Email",
        required=True,
        help_text="Required. Enter a valid email address."
    )
    send_email = BooleanField(
        label="Send email",
        required=False,
        initial=True,
        help_text="Send an email to the user with a link to set their password and log in.",
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'avatar', 'send_email')
        labels = {
            'phone': 'Phone number',
            'avatar': 'Avatar'
        }


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'avatar')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email field is required.")
        return email


class UserChangeForm(forms.ModelForm):
    pass
    # kg = Country.objects.get(country_code='kg')
    # clubs = []
    # for i in kg.city_set.all():
    #     for c in i.club_set.all():
    #         club = c.pk, c.name
    #         clubs.append(club)
    # s_clubs = sorted(clubs, key=lambda tup: tup[1])
    #
    # coach_club = forms.MultipleChoiceField(choices=s_clubs, label='Клуб', widget=forms.SelectMultiple(),
    #                                        required=False)
    #
    # class Meta:
    #     model = User
    #     fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'avatar')
    #     labels = {'username': 'Логин', 'first_name': 'Имя', 'last_name': 'Фамилия', 'email': 'Email',
    #               'phone': 'Номер телефона', 'avatar': 'Фотография'}
    #
    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if not email:
    #         raise ValidationError("Email field is required.")
    #     return email
