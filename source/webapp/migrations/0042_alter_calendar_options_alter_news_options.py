# Generated by Django 4.1.7 on 2023-03-28 22:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0041_remove_player_patronymic'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='calendar',
            options={'permissions': (('view_deleted_events', 'can view list of deleted events'),), 'verbose_name': 'Событие', 'verbose_name_plural': 'События'},
        ),
        migrations.AlterModelOptions(
            name='news',
            options={'permissions': (('view_deleted_news', 'can view list of deleted news'),), 'verbose_name': 'Новость', 'verbose_name_plural': 'Новости'},
        ),
    ]
