from doctocnet.settings import *

SITE_ID = config('SITE_ID_4', cast=int, default=4)
ROOT_URLCONF = config('ROOT_URLCONF_4', default='doctocnet.urls')
LOG_FILE = os.path.join(DJANGO_LOG_DIR, f"django{SITE_ID}.log")
LANGUAGE_CODE = config('LANGUAGE_CODE_4', default='en')

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
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'filters': ['require_debug_true'],
    },
        "console_debug_false": {
            "level": LOG_LEVEL,
            "filters": ["require_debug_false"],
            "class": "logging.StreamHandler",
        },

        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        },
        "applogfile": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOG_FILE,
        },
        "django.server": DEFAULT_LOGGING["handlers"]["django.server"],
    },

    "loggers": {
        '': {
            'level': LOG_LEVEL,
            'handlers': ['console', 'console_debug_false', 'applogfile',],
            'propagate': True,
        },
        "django": {
            "handlers": [
                "console",
                "console_debug_false",
                "mail_admins",
                "applogfile",
            ],
            "level": LOG_LEVEL,
        },
        "bot.stream": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "bot.tasks": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "bot.doctoctocbot": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "messenger.tasks": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "tagging.tasks": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "timeline": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "django-invitations": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "bot.bin.thread": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "moderation.tasks": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "moderation.moderate": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "moderation.social": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "request.tasks": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "dm": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "autotweet": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
            "level": LOG_LEVEL,
        },
        "django.server": DEFAULT_LOGGING["loggers"]["django.server"],
    },
}
logging.config.dictConfig(DICT_CONFIG)