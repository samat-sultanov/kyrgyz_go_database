# Generated by Django 4.1.7 on 2023-03-31 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0046_merge_0044_partner_0045_alter_calendar_deadline'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerintournament',
            name='GoLevel_after',
            field=models.CharField(default=0, max_length=3, verbose_name='GoLevel'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='playerintournament',
            name='GoLevel',
            field=models.CharField(default=0, max_length=3, verbose_name='GoLevel'),
            preserve_default=False,
        ),
    ]
