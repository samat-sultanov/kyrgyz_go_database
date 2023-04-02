from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='email')
    avatar = models.ImageField(null=True, blank=True, upload_to='user_avatar', verbose_name="Аватар")
    phone = models.CharField(max_length=50, null=True, blank=True, verbose_name='Номер телефона')

    def __str__(self):
        return f'{self.username}'
