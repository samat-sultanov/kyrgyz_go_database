import os
from datetime import datetime as dt
import datetime

from PIL import Image
from phonenumber_field.modelfields import PhoneNumberField

from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from django.dispatch import receiver

from accounts.models import User

DEFAULT_CLASS = 'all'
CLASS_CHOICES = ((DEFAULT_CLASS, 'Все классы'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'),)
STATUS = [('Confirmed', 'Confirmed'), ('Not confirmed', 'Not confirmed')]
DAYS = [('Пн', 'Пн'), ('Вт', 'Вт'), ('Ср', 'Ср'), ('Чт', 'Чт'), ('Пт', 'Пт'), ('Сб', 'Сб'), ('Вс', 'Вс')]


class Country(models.Model):
    country_code = models.CharField(verbose_name='Country', max_length=2)

    def __str__(self):
        return f'{self.country_code}'

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"


class City(models.Model):
    city = models.CharField(verbose_name="Город", max_length=50)
    country = models.ForeignKey('webapp.Country', on_delete=models.CASCADE)
    region = models.ForeignKey('webapp.Region', default=1, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.city}'

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"


class Region(models.Model):
    name = models.CharField(verbose_name="Регион", max_length=50, null=False, blank=False)
    country = models.ForeignKey('webapp.Country', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"


class DayOfWeek(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.name}'


class Club(models.Model):
    logo = models.ImageField(verbose_name='Лого', null=True, blank=True, upload_to='club_logo')
    name = models.CharField(verbose_name="Club title", max_length=50, null=True, blank=True)
    EGDName = models.CharField(verbose_name='EGDName', max_length=6, null=True, blank=True)
    city = models.ForeignKey('webapp.City', on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey('webapp.Country', on_delete=models.CASCADE, null=True, blank=True)
    region = models.ForeignKey('webapp.Region', on_delete=models.CASCADE, null=True, blank=True)
    coaches = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='clubs')
    num_players = models.PositiveIntegerField(null=True, blank=True, verbose_name='Количество участников клуба')
    address = models.CharField(verbose_name='Address', max_length=50, null=True, blank=True)
    phonenumber = PhoneNumberField(verbose_name='Номер телефона', null=True, blank=True)
    web_link = models.URLField(verbose_name='Интернет-ссылка', null=True, blank=True)
    schedule_from = models.TimeField(verbose_name='С', null=True, blank=True)
    schedule_to = models.TimeField(verbose_name='До', null=True, blank=True)
    breakfast_from = models.TimeField(verbose_name='Обед c', null=True, blank=True)
    breakfast_to = models.TimeField(verbose_name='до', null=True, blank=True)
    days_of_work = models.ManyToManyField(DayOfWeek, related_name='days_of_work', blank=True, null=True)
    day_of_week = models.ManyToManyField(DayOfWeek, related_name='day_of_week', blank=True, null=True)



    def __str__(self):
        return f'{self.id}. {self.name} - {self.EGDName}'

    class Meta:
        verbose_name = "Клуб"
        verbose_name_plural = "Клубы"

    def save(self, *args, **kwargs):
        super(Club, self).save(*args, **kwargs)
        if self.logo:
            img = Image.open(self.logo.path)
            if img.height > 500 or img.width > 500:
                output_size = (500, 500)
                img.thumbnail(output_size)
                img.save(self.logo.path)


class Game(models.Model):
    black = models.ForeignKey('webapp.Player', on_delete=models.CASCADE, related_name="black_player", null=True,
                              blank=True)
    white = models.ForeignKey('webapp.Player', on_delete=models.CASCADE, related_name="white_player", null=True,
                              blank=True)
    result = models.CharField(verbose_name="Result", max_length=10, null=True, blank=True)
    black_score = models.PositiveIntegerField(verbose_name="Black score", null=True, blank=True)
    white_score = models.PositiveIntegerField(verbose_name='White score', null=True, blank=True)
    board_number = models.PositiveIntegerField(verbose_name="BoardNumber", default=0)
    date = models.DateTimeField(verbose_name='Date')
    tournament = models.ForeignKey('webapp.Tournament', on_delete=models.CASCADE)
    round_num = models.PositiveIntegerField(verbose_name="Round")
    black_gor_change = models.FloatField(verbose_name='Black GoR change', null=True, blank=True)
    white_gor_change = models.FloatField(verbose_name='White GoR change', null=True, blank=True)

    def __str__(self):
        return f'{self.id}. {self.black} : {self.white} = {self.result}'

    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"


class Tournament(models.Model):
    name = models.CharField(verbose_name="Tournament name", max_length=50, null=True, blank=True)
    city = models.ForeignKey('webapp.City', on_delete=models.CASCADE, null=True, blank=True)
    region = models.ForeignKey('webapp.Region', on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(verbose_name="Место проведения", max_length=100, null=True, blank=True)
    board_size = models.PositiveIntegerField(verbose_name="Board size", default=19)
    rounds = models.PositiveIntegerField(verbose_name='Total rounds')
    date = models.DateField(verbose_name="Date", null=True, blank=True)
    tournament_class = models.CharField(max_length=20, default=DEFAULT_CLASS, choices=CLASS_CHOICES,
                                        verbose_name='Class', blank=True, null=True)
    regulations = models.TextField(verbose_name='Regulations', null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, default=1,
                                    verbose_name="Автор")

    def __str__(self):
        return f'{self.id}. {self.name} - {self.board_size}'

    class Meta:
        verbose_name = "Турнир"
        verbose_name_plural = "Турниры"


class Player(models.Model):
    avatar = models.ImageField(null=True, blank=True, upload_to='user_avatar', verbose_name='Аватар')
    first_name = models.CharField(verbose_name="Имя", max_length=50, blank=True, null=True)
    last_name = models.CharField(verbose_name="Фамилия", max_length=50, blank=True, null=True)
    clubs = models.ManyToManyField('webapp.Club', related_name='players', blank=True)
    country = models.ForeignKey('webapp.Country', on_delete=models.CASCADE)
    tournaments = models.ManyToManyField('webapp.Tournament', through='webapp.PlayerInTournament')
    city = models.ForeignKey('webapp.City', on_delete=models.CASCADE, blank=True, null=True)
    birth_date = models.DateField(verbose_name="Дата рождения", blank=True, null=True)
    current_rank = models.CharField(verbose_name='GoLevel', max_length=3, null=True, blank=True, default='0k')
    current_rating = models.IntegerField(verbose_name='Rating', null=True, blank=True, default=0)
    EgdPin = models.PositiveIntegerField(verbose_name='EgdPin', blank=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.last_name} {self.first_name} {self.current_rank}'

    def get_total_tournaments(self):
        return self.tournaments.count()

    def get_total_clubs(self):
        return self.clubs.count()

    def get_age_date(self):
        today = datetime.date.today()
        days_age = (today - self.birth_date)
        age = (days_age.days // 365)
        return age

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"

    def save(self, *args, **kwargs):
        super(Player, self).save(*args, **kwargs)
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 500 or img.width > 500:
                output_size = (500, 500)
                img.thumbnail(output_size)
                img.save(self.avatar.path)


class Recommendation(models.Model):
    text = models.TextField(max_length=400, verbose_name='Рекомендация')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, default=1, related_name='author',
                               verbose_name="Автор")
    player = models.ForeignKey('webapp.Player', on_delete=models.CASCADE, related_name='player',
                               verbose_name="Игрок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время изменения")

    def __str__(self):
        return f'{self.pk}. {self.text[:20]}'

    class Meta:
        verbose_name = "Рекомендация"
        verbose_name_plural = "Рекомендации"


class PlayerInTournament(models.Model):
    game_id = models.PositiveIntegerField(verbose_name="ID in tournament(id_in_tournament)")
    player = models.ForeignKey('webapp.Player', on_delete=models.CASCADE)
    tournament = models.ForeignKey('webapp.Tournament', on_delete=models.CASCADE)
    GoLevel = models.CharField(verbose_name='GoLevel', max_length=3, default='10k')
    GoLevel_after = models.CharField(verbose_name='GoLevel', max_length=3, blank=True, null=True)
    rating = models.IntegerField(verbose_name='Rating', blank=True, null=True)
    rating_after = models.IntegerField(verbose_name='Rating after', blank=True, null=True)
    club = models.ForeignKey('webapp.Club', on_delete=models.CASCADE, blank=True, null=True)
    position = models.PositiveIntegerField(verbose_name='Позиция/место', default=0)
    results = models.CharField(verbose_name='results by round', max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.id} - {self.player}: {self.tournament}, {self.GoLevel}'


class File(models.Model):
    file = models.FileField(upload_to='files/', null=True, validators=[
        FileExtensionValidator(allowed_extensions=['xml'], message=['Загрузите файл в формате XML'],
                               code='invalid_extension')])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super(File, self).delete(*args, **kwargs)


class News(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок новости')
    text = models.TextField(max_length=5000, verbose_name='Текст новости')
    author = models.ForeignKey('accounts.User', on_delete=models.SET_DEFAULT, default=1, related_name='news',
                               verbose_name='Автор новости')
    news_image = models.ImageField(verbose_name='Изображение', null=True, blank=True, upload_to='news_images')
    video_link = models.URLField(verbose_name='Ссылка на видео', null=True, blank=True)
    is_deleted = models.BooleanField(default=False, verbose_name='Удален')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время изменения")

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        permissions = (("view_deleted_news", "can view list of deleted news"),)

    def __str__(self):
        return f'{self.title} - {self.created_at.strftime("%d-%m-%Y %H:%M:%S")}'

    def get_absolute_url(self):
        return reverse('webapp:news_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        super(News, self).save(*args, **kwargs)
        if self.news_image:
            img = Image.open(self.news_image.path)
            if img.height > 1500 or img.width > 1500:
                output_size = (1500, 1500)
                img.thumbnail(output_size)
                img.save(self.news_image.path)


def get_author():
    return User.objects.first()


class Calendar(models.Model):
    event_name = models.CharField(max_length=100, verbose_name='Название события', null=False, blank=False)
    event_city = models.CharField(max_length=50, verbose_name='Город проведения', null=False, blank=False)
    event_date = models.DateField(verbose_name='Дата проведения', null=False, blank=False)
    text = models.TextField(max_length=5000, verbose_name='Описание события')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET(get_author), verbose_name='Автор',
                               default=get_author)
    calendar_image = models.ImageField(verbose_name='Изображение', null=True, blank=True, upload_to='calendar_images')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_deleted = models.BooleanField(default=False, verbose_name='Удален')
    deadline = models.DateField(verbose_name='Дата окончания регистрации', null=False, blank=False)

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        permissions = (("view_deleted_events", "can view list of deleted events"),)

    def is_end_date(self):
        return dt.now().date() > self.deadline

    def save(self, *args, **kwargs):
        super(Calendar, self).save(*args, **kwargs)
        if self.calendar_image:
            img = Image.open(self.calendar_image.path)
            if img.height > 1500 or img.width > 1500:
                output_size = (1500, 1500)
                img.thumbnail(output_size)
                img.save(self.calendar_image.path)


class Participant(models.Model):
    name = models.CharField(max_length=20, verbose_name='Имя', null=False, blank=False)
    surname = models.CharField(max_length=20, verbose_name='Фамилия', null=False, blank=False)
    rank = models.CharField(max_length=3, verbose_name='GoLevel', null=False, blank=False)
    event = models.ForeignKey('webapp.Calendar', on_delete=models.CASCADE, related_name='participant')
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name='Город')
    phonenumber = PhoneNumberField(verbose_name='Номер телефона'
                                   , null=True, blank=False, max_length=16, default=None)
    status = models.CharField(max_length=50, default=STATUS[1][1], choices=STATUS, verbose_name='Статус')

    class Meta:
        db_table = "participant"
        verbose_name = "Участник"
        verbose_name_plural = "Участники"

    def __str__(self):
        return f'{self.id} - {self.surname}: {self.name}'


class Partner(models.Model):
    name = models.CharField(max_length=100, verbose_name="Наименование партнера", null=False, blank=False)
    logo = models.ImageField(verbose_name='Лого', null=False, blank=False, upload_to='partner_logo')
    web_link = models.URLField(verbose_name='Интернет-ссылка', null=True, blank=True)

    def __str__(self):
        return f'{self.id}. {self.name[:30]}'

    class Meta:
        db_table = "partner"
        verbose_name = "Партнер"
        verbose_name_plural = "Партнеры"

    def save(self, *args, **kwargs):
        super(Partner, self).save(*args, **kwargs)
        if self.logo:
            img = Image.open(self.logo.path)
            if img.height > 500 or img.width > 500:
                output_size = (500, 500)
                img.thumbnail(output_size)
                img.save(self.logo.path)


class NotModeratedTournament(models.Model):
    name = models.CharField(verbose_name="Tournament name", max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date of upload')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, default=1,
                                    verbose_name="Uploaded by")

    def __str__(self):
        return f'{self.id}. {self.name[:30]}: {self.uploaded_by}'

    class Meta:
        db_table = "moderation"
        verbose_name = "TournamentForModeration"
        verbose_name_plural = "TournamentsForModeration"


@receiver(models.signals.post_delete, sender=News)
def auto_delete_img_on_delete(sender, instance, **kwargs):
    if instance.news_image:
        if os.path.isfile(instance.news_image.path):
            os.remove(instance.news_image.path)


@receiver(models.signals.pre_save, sender=News)
def auto_delete_img_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    old_img = News.objects.get(pk=instance.pk).news_image

    if old_img:
        new_img = instance.news_image
        if not old_img == new_img:
            if os.path.isfile(old_img.path):
                os.remove(old_img.path)
