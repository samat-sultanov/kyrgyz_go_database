from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth import get_user_model

from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone', 'avatar',
                       'send_email'),
        }),
    )
    form = CustomUserChangeForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if form.cleaned_data.get('send_email', False):
            token = default_token_generator.make_token(obj)
            uid = urlsafe_base64_encode(force_bytes(obj.pk))
            url = reverse('password_reset_confirm', args=[uid, token])
            reset_url = request.build_absolute_uri(url)

            subject = 'Активация аккаунта'
            message = f'Уважаемый {User.username}!' \
                      f'Для активации аккаунта пройдите по следующей ссылке: {reset_url}'
            from_email = 'kyrgyzgodatabase@gmail.com'
            recipient_list = [obj.email]
            send_mail(subject, message, from_email, recipient_list)


User = get_user_model()
admin.site.register(User, CustomUserAdmin)
