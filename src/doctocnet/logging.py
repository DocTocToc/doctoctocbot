from django.utils.log import DEFAULT_LOGGING
import sys

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
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
        "django.server": DEFAULT_LOGGING['formatters']['django.server'],
    },

    "handlers": {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'filters': ['require_debug_true'],
    },

        "console_debug_false": {
            "level": "INFO",
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
        "django.server": DEFAULT_LOGGING["loggers"]["django.server"],
    },
}