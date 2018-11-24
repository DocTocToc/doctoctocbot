import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctocnet.settings')

app = Celery('quick_publisher')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    #'dm-every-3-minutes': {
    #    'task': 'dm.tasks.directmessages',
    #    'schedule': 180.0,
    #    'args': None,
    #    },
    'poll-moderation-dm-every-1-minute': {
        'task': 'moderation.tasks.poll_moderation_dm',
        'schedule': 60.0,
        'args': None,
        },
    'normalize-every-1-minute': {
        'task': 'conversation.tasks.handle_allnormalize',
        'schedule': 180.0,
        'args': None,
        }
    }