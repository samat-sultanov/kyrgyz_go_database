from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image
from sorl.thumbnail import delete
from django.dispatch import receiver



class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='email')
    avatar = models.ImageField(null=True, blank=True, upload_to='user_avatar', verbose_name="Аватар")
    phone = PhoneNumberField(unique=True, verbose_name='Номер телефона', null=True, blank=True, max_length=16)

    def __str__(self):
        return f'{self.username}'

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 500 or img.width > 500:
                output_size = (500, 500)
                img.thumbnail(output_size)
                img.save(self.avatar.path)

@receiver(models.signals.pre_save, sender=User)
def delete_old_image_cache(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        if old_instance.avatar:
            if old_instance.avatar != instance.avatar:
                delete(old_instance.avatar)