# Generated by Django 4.1.7 on 2023-04-21 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0059_notmoderatedtournament'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournament',
            name='is_moderated',
        ),
    ]
