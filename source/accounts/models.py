from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='email')
    avatar = models.ImageField(null=True, blank=True, upload_to='user_avatar', verbose_name="Аватар")
    phone = PhoneNumberField(unique=True, verbose_name='Номер телефона', null=True, blank=True, max_length=16)

    def __str__(self):
        return f'{self.username}'
