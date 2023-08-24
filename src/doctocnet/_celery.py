from __future__ import absolute_import,  unicode_literals
import os
import logging
from logging.handlers import RotatingFileHandler
from celery import Celery
from celery.schedules import crontab
from celery.signals import after_setup_logger, after_setup_task_logger

from django.conf import settings

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctocnet.settings')

app = Celery('doctocnet')
app.config_from_object('django.conf:settings', namespace="CELERY")
app.autodiscover_tasks()

@after_setup_task_logger.connect
def after_setup_celery_task_logger(logger, **kwargs):
    """ This function sets the 'celery.task' logger handler and formatter """
    create_celery_logger_handler(logger, True)


@after_setup_logger.connect
def after_setup_celery_logger(logger, **kwargs):
    """ This function sets the 'celery' logger handler and formatter """
    create_celery_logger_handler(logger, False)

def create_celery_logger_handler(logger, propagate):
    # 209715200 is 1024 * 1024 * 200 or 200 MB, same as in settings
    celery_handler = RotatingFileHandler(
        settings.CELERY_LOG_FILE,
        maxBytes=209715200,
        backupCount=10
    )
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    #celery_formatter = jsonlogger.JsonFormatter(settings.LOGGING['formatters']['json']['format'])
    celery_handler.setFormatter(formatter)

    logger.addHandler(celery_handler)
    logger.logLevel = settings.LOG_LEVEL
    logger.propagate = propagate

if __name__ == '__main__':
    app.start()