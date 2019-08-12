from dm.retrieve import savedm
from celery import shared_task



@shared_task
def directmessages():
    savedm()