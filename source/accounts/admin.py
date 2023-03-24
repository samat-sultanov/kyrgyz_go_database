from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .models import User


class CustomUserAdmin(admin.ModelAdmin):
    model = User
    fields = ['username', 'email', 'password']


admin.site.register(User, CustomUserAdmin)
