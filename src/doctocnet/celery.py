import os
from celery import Celery

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctocnet.settings.development')

app = Celery('quick_publisher')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'dm-every-10-minutes': {
        'task': 'dm.tasks.directmessages',
        'schedule': 600.0,
        'args': None,
        },
    'poll-moderation-dm-every-10-minute': {
        'task': 'moderation.tasks.poll_moderation_dm',
        'schedule': 600.0,
        'args': None,
        },
    'normalize-every-10-minute': {
        'task': 'conversation.tasks.handle_allnormalize',
        'schedule': 600.0,
        'args': None,
        },
    'handle_record_timeline': {
        'task': 'timeline.tasks.handle_record_timeline',
        'schedule': 60.0,
        'args': None,
        },
    'handle_scrape_web_roots': {
        'task': 'display.tasks.handle_scrape_web_roots',
        'schedule': 60.0,
        'args': (settings.SCRAPING_HOUR_DELTA,)
        },
    'handle_scrape_web_timeline': {
        'task': 'display.tasks.handle_scrape_web_timeline',
        'schedule': 60.0,
        'args': (settings.SCRAPING_HOUR_DELTA,)
        },
    }