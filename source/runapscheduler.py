import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

logger = logging.getLogger(__name__)


def rank_sync_with_egd_job():
    # Your job processing logic here...
    pass


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
            delete_old_job_executions,
            trigger=CronTrigger(month=1, day=1, hour="02", minute="00"),
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
