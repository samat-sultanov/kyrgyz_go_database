import logging
import requests

from django.conf import settings
from django.utils import timezone

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from webapp.models import Player

logger = logging.getLogger(__name__)


def rank_sync_with_egd_job():
    all_players = Player.objects.all()
    for player in all_players:
        if player.EgdPin == 0:
            continue
        else:
            payload = {'pin': player.EgdPin}
            request_to_egd = requests.get('https://www.europeangodatabase.eu/EGD/GetPlayerDataByPIN.php',
                                          params=payload)
            if request_to_egd.status_code >= 500:
                with open('rating_job_errors_log.txt', 'a') as f:
                    f.write(f"\n{timezone.now()}: Ошибка со стороны egd. Код ошибки: {request_to_egd.status_code}. "
                            f"Ошибка произошла при итерации: '{player.first_name} "
                            f"{player.last_name} ПИН: {player.EgdPin}'\n_______________________________________\n")
                continue

            elif request_to_egd.status_code == 200:
                player_egd_data = request_to_egd.json()
                if player_egd_data.get('retcode') == "Ok":
                    if player.current_rating == int(player_egd_data.get('Gor')):
                        continue
                    else:
                        player.current_rank = player_egd_data.get('Grade')
                        player.current_rating = int(player_egd_data.get('Gor'))
                        player.save()
                else:
                    with open('rating_job_errors_log.txt', 'a') as f:
                        f.write(f"\n{timezone.now()}: Очень странно. По ПИНу '{player.EgdPin}' игрока "
                                f"'{player.last_name} {player.first_name}' еропейская база не возвратила данные. "
                                f"Т.е. не нашла игрока в базе egd. Возможно в нашей базе ПИН введен "
                                f"неправильно\n_______________________________________\n")
                    continue
            else:
                with open('rating_job_errors_log.txt', 'a') as f:
                    f.write(f"\n{timezone.now()}: Невыясненная ошибка. Код ошибки: {request_to_egd.status_code}. "
                            f"Следует взглянуть в логи nginx`а. "
                            f"Ошибка произошла при итерации: '{player.first_name} {player.last_name} "
                            f"ПИН: {player.EgdPin}'\n_______________________________________\n")
                continue


def sync_pin_job():
    players_with_no_pin = Player.objects.all().filter(EgdPin=0)
    for player in players_with_no_pin:
        payload = {'lastname': player.last_name, 'name': player.first_name}
        request_to_egd = requests.get('https://www.europeangodatabase.eu/EGD/GetPlayerDataByData.php', params=payload)
        if request_to_egd.status_code == 200:
            if request_to_egd.json().get("retcode") == "Ok":
                egd_response_players_list = request_to_egd.json().get("players")
                counter = 0
                temp_matching_player = None
                for player_in_list in egd_response_players_list:
                    if player_in_list.get('lastname') == player.last_name and player_in_list.get(
                            'name') == player.first_name:
                        temp_matching_player = player_in_list
                        counter += 1
                if counter == 1:
                    egd_player_pin = int(temp_matching_player.get('Pin_Player'))
                    player.EgdPin = egd_player_pin
                    player.save()
                elif counter > 1:
                    with open('pin_job_errors_log.txt', 'a') as f:
                        f.write(f"\n{timezone.now()}: В egd найдено больше одного игрока с фамилией и именем: "
                                f"'{player.last_name} {player.first_name}'"
                                f"\n_______________________________________\n")
                    continue
                else:
                    with open('pin_job_errors_log.txt', 'a') as f:
                        f.write(
                            f"\n{timezone.now()}: В egd не нашелся точно совпадающий игрок "
                            f"'{player.last_name} {player.first_name}'. Но нашлись с очень похожими именамии фамилиями."
                            f" Проверьте через api: https://www.europeangodatabase.eu/EGD/how_to_use_GetData.html "
                            f"\n_______________________________________\n")
                    continue
            else:
                with open('pin_job_errors_log.txt', 'a') as f:
                    f.write(f"\n{timezone.now()}: Игрок '{player.last_name} {player.first_name}' не найден в egd."
                            f"\n_______________________________________\n")
                continue
        else:
            with open('pin_job_errors_log.txt', 'a') as f:
                f.write(f"\n{timezone.now()}: Или egd не доступен или у вас проблемы с сетью. "
                        f"Status code: {request_to_egd.status_code}. "
                        f"Ошибка произошла при итерации: {player.first_name} "
                        f"{player.last_name}\n_______________________________________\n")
            continue


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            rank_sync_with_egd_job,
            trigger=CronTrigger(day="last", hour=3, minute=0),
            id="rank_sync_with_egd_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'rank_sync_with_egd_job'.")

        scheduler.add_job(
            sync_pin_job,
            trigger=CronTrigger(day_of_week="mon", hour=5, minute=0),
            id="sync_pin_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'sync_pin_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=IntervalTrigger(days=1461, start_date='2023-01-01 00:00:00'),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added yearly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
