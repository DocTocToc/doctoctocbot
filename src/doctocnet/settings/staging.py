from pathlib import Path
from decouple import AutoConfig, Csv
from dj_database_url import parse as db_url
from django.utils.log import DEFAULT_LOGGING
import logging

from .base import *

LOGLEVEL = "DEBUG"
DICT_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s %(name)s %(pathname)s:%(lineno)s:%(funcName)s %(levelname)s %(message)s",
        },
        "django.server": DEFAULT_LOGGING['formatters']['django.server'],
    },

    "handlers": {
        'console': {
            'level': (LOGLEVEL or "DEBUG"),
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'filters': ['require_debug_true'],
    },

        "console_debug_false": {
            "level": (LOGLEVEL or "INFO"),
            "filters": ["require_debug_false"],
            "class": "logging.StreamHandler",
        },

        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        },
        
        "django.server": DEFAULT_LOGGING["handlers"]["django.server"],

    },

    "loggers": {
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        "django": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": 'INFO',
        },
        "bot.stream": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": 'INFO',
        },
        "django.server": DEFAULT_LOGGING["loggers"]["django.server"],
    },
}
logging.config.dictConfig(DICT_CONFIG)


CONFIG_DIR = Path("/home/elkcloner/.doctocnet/staging")
config = AutoConfig(search_path = CONFIG_DIR)

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS += ['staging.doctoctoc.net']

SITE_ID = 2

INSTALLED_APPS += [
    'django_extensions',
    'status',
    'gpgcontact',
]

DATABASES = {
    'default': config(
        'DATABASE_URL',
        #default='',
        cast=db_url
    ),
    'status': config(
    'DATABASE_URL_PRODSTATUS',
    #default='',
    cast=db_url
    ),
}

STATICFILES_DIRS = [
        ]

STATIC_ROOT = config('STATIC_ROOT')
STATIC_URL='/static/'

MEDIA_ROOT='/var/opt/doctocnet/media'
MEDIA_URL='/media/'

# Postgres
POSTGRESQL = {
    "username":"doctoctoctest",
    "password":"doctoctoctest",
    "host":"127.0.0.1",
    "port":"5432",
    "database":"status"
}

STRIPE_PUBLIC_KEY = config("STRIPE_TEST_PUBLIC_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_TEST_SECRET_KEY", default="")
STRIPE_LIVE_MODE = False

# BOT settings
# Path on disk where images are saved
TWITTER_CONSUMER_KEY = config('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = config('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN = config('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = config('TWITTER_ACCESS_TOKEN_SECRET')
BOT_IMAGES_PATH = config('BOT_IMAGES_PATH', default = "~/Pictures")
BOT_ID = config('BOT_ID', cast=int)
BOT_SCREEN_NAME = config('BOT_SCREEN_NAME')
KEYWORD_TRACK_LIST = ["doctoctoc", "docstoctoc"]
KEYWORD_RETWEET_LIST = ["#doctoctoc",]
NUMBER_OF_RT = 20
TWEET_LANGUAGE = ""

# backend bot Twitter API credentials
BACKEND_TWITTER_CONSUMER_KEY = config('BACKEND_TWITTER_CONSUMER_KEY')
BACKEND_TWITTER_CONSUMER_SECRET = config('BACKEND_TWITTER_CONSUMER_SECRET')
BACKEND_TWITTER_ACCESS_TOKEN = config('BACKEND_TWITTER_ACCESS_TOKEN')
BACKEND_TWITTER_ACCESS_TOKEN_SECRET = config('BACKEND_TWITTER_ACCESS_TOKEN_SECRET')

# Twitter key (social-auth-app-django)
SOCIAL_AUTH_TWITTER_KEY = config('TWITTER_CONSUMER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = config('TWITTER_CONSUMER_SECRET')

# gpgcontact
GNUPGHOME = config('GNUPGHOME')
GNUPG_PUBLIC_KEYS = config('GNUPG_PUBLIC_KEYS', cast=Csv())