from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0012_merge_20230306_2358'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='club',
            name='club_go_level',
        ),
        migrations.RemoveField(
            model_name='club',
            name='club_players',
        ),
        migrations.AlterField(
            model_name='player',
            name='clubs',
            field=models.ManyToManyField(blank=True, related_name='players', to='webapp.club'),
        ),
    ]
