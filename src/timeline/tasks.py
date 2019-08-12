from celery import shared_task

from bot.bin.timeline import record_timeline


@shared_task
def handle_record_timeline():
    record_timeline()