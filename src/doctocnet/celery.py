from __future__ import absolute_import
import os
from celery import Celery

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctocnet.settings.development')

app = Celery('quick_publisher')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'poll-dm': {
        'task': 'dm.tasks.directmessages',
        'schedule': settings.BEAT_PERIOD.get('poll_dm', 600.0),
        'args': None,
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
    }