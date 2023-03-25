from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone', 'avatar'),
        }),
    )
    form = CustomUserChangeForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(User, CustomUserAdmin)
