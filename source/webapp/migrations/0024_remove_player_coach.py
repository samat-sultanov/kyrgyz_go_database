# Generated by Django 4.1.7 on 2023-03-18 18:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0023_merge_20230318_1642'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='coach',
        ),
    ]
