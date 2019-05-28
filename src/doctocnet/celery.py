from __future__ import absolute_import
import os
import logging
from logging.handlers import RotatingFileHandler
from celery import Celery
from celery.schedules import crontab
from celery.signals import after_setup_logger, after_setup_task_logger

from django.conf import settings

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

app = Celery('doctocnet')
app.config_from_object('django.conf:settings')

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

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
"""
app.conf.beat_schedule = {
    'poll-dm': {
        'task': 'dm.tasks.directmessages',
        'schedule': settings.BEAT_PERIOD.get('poll_dm', 600.0),
        'args': None,
        'options': {
                    'expires': 15*60,
                    },
        },
    'poll-moderation-dm': {
        'task': 'moderation.tasks.poll_moderation_dm',
        'schedule': settings.BEAT_PERIOD.get('poll_moderation_dm', 600.0),
        'args': None,
        },
    'normalize': {
        'task': 'conversation.tasks.handle_allnormalize',
        'schedule': settings.BEAT_PERIOD.get('normalize', 600.0),
        'args': None,
        },
    'record-timeline': {
        'task': 'timeline.tasks.handle_record_timeline',
        'schedule': settings.BEAT_PERIOD.get('record_timeline', 60.0),
        'args': None,
        },
#    'handle_scrape_web_roots': {
#        'task': 'display.tasks.handle_scrape_web_roots',
#        'schedule': 60.0,
#        'args': (settings.SCRAPING_HOUR_DELTA,)
#        },
    'scrape-web-timeline': {
        'task': 'display.tasks.handle_scrape_web_timeline',
        'schedule': settings.BEAT_PERIOD.get('scrape_web_timeline', 120),
        'args': (settings.SCRAPING_HOUR_DELTA,)
        },
    'update-trees': {
        'task': 'conversation.tasks.handle_update_trees',
        'schedule': settings.BEAT_PERIOD.get('update_trees', 120),
        'args': (settings.SCRAPING_HOUR_DELTA,)
        },
    'poll-lists-members': {
        'task': 'moderation.tasks.handle_poll_lists_members',
        'schedule': settings.BEAT_PERIOD.get('poll_lists_members', 900),
        'args': None,
        },
    'backup-lists': {
        'task': 'moderation.tasks.handle_backup_lists',
        'schedule': crontab(hour=4, minute=0),
        'args': None,
        },
    'create-update-lists': {
        'task': 'moderation.tasks.handle_create_update_lists',
        'schedule': crontab(hour=4, minute=0),
        'args': None,
        },
    }
"""