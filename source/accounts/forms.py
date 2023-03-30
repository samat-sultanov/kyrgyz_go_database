from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import EmailField, BooleanField

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


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'avatar')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email field is required.")
        return email


