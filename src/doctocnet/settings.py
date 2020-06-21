from django.utils.translation import gettext_lazy as _
import os
import logging
from django.utils.log import DEFAULT_LOGGING
from decouple import AutoConfig, Csv
from pathlib import Path

mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING) 

logger = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CONFIG_DIR = Path(BASE_DIR + "/..")
config = AutoConfig(search_path = CONFIG_DIR)

DEBUG = config('DEBUG', default=True, cast=bool)

DEBUG_HTTPS = config('DEBUG_HTTPS', default=False, cast=bool)

LOG_LEVEL = config('LOG_LEVEL', default='DEBUG')

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
        
        "django.server": DEFAULT_LOGGING["handlers"]["django.server"],

    },

    "loggers": {
        '': {
            'level': LOG_LEVEL,
            'handlers': ['console', 'console_debug_false'],
            'propagate': False,
        },
        "django": {
            "handlers": ["console", "console_debug_false", "mail_admins"],
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
        "django.server": DEFAULT_LOGGING["loggers"]["django.server"],
    },
}
logging.config.dictConfig(DICT_CONFIG)

#sys.path.append(os.path.dirname(os.path.abspath(__file__)))





SECRET_KEY = config('SECRET_KEY')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default="*")

if not DEBUG or DEBUG_HTTPS:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SITE_ID = config('SITE_ID_1', cast=int, default=1)

# WAGTAIL
WAGTAIL_SITE_NAME = config('WAGTAIL_SITE_NAME')
WAGTAIL_FRONTEND_LOGIN_URL = '/accounts/login/'

# Application definition

INSTALLED_APPS = [
    'invitations',
    'users',
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'constance',
    'rest_framework',
    'doctocnet',
    'landing',
    'social_django',
    'moderation',
    'conversation',
    'bot',
    'dm',
    'charts',
    'display',
    'timeline',
    'crispy_forms',
    'crowdfunding',
    'registration',
    'django_countries',
    'customer',
    'mptt',
    'dry_rest_permissions',
    #'corsheaders',
    'django_celery_beat',
    'messenger',
    'rangefilter',
    'dashboard',
# wagtail start
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',
    
    'modelcluster',
    'taggit',
# wagtail stop
# wagtail blog
    'blog',
    'meta',
    'wagtailmetadata',
    'ajax_select',
# wagtail blog stop
    'link',
    'gpgcontact',
    'community',
    'discourse',
    'mesh',
    'tagging',
    'markdownify',
    'optin',
    'bootstrap_modal_forms',
    'dal',
    'dal_select2',
    'silver',
    'rest_framework.authtoken',
    'request',
    'invite',
    'django.contrib.humanize',
    'hcp',
    'authorize',
    'constance.backends.database',
    'autotweet',
    'reversion',
    'markdown',
]

if DEBUG:
    INSTALLED_APPS += [
        'django_extensions',
        'corsheaders',
    ]

MIDDLEWARE = [


    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
# wagtail start
    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
# wagtail stop
]

if DEBUG:
    MIDDLEWARE += [
        'corsheaders.middleware.CorsMiddleware',
    ]

ROOT_URLCONF = 'doctocnet.urls'

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            'templates',     
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'django.template.context_processors.media',
                'doctocnet.context_processors.site',
            ],
        },
    },
]

WSGI_APPLICATION = 'doctocnet.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DATABASE_NAME', default='postgres'),
        'USER': config('DATABASE_USER', default='postgres'),
        'PASSWORD': config('DATABASE_PASSWORD', default=''),
        'HOST': config('DATABASE_HOST', default='database'),
        'PORT': config('DATABASE_PORT', cast=int, default=5432),
        'OPTIONS': {
            'connect_timeout': config('DATABASE_CONNECTION_TIMEOUT', default=10),
        },
    }
}

STATIC_ROOT = config('STATIC_ROOT')
STATIC_URL = '/static/'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/
LANGUAGE_CODE = 'fr'

LANGUAGES = [
    ('fr', _('French')),
    ('en', _('English')),
]
# Model Translation
MODELTRANSLATION_FALLBACK_LANGUAGES = {'default': ('en', 'fr'), 'fr': ('en',)}

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
    "templates/locale",
]
# use this locale to sort localized strings, default to 'en_US.UTF-8'
# you have to generate the locales you will use on your GNU/Linux server:
# $ locale-gen fr_FR.UTF-8
# $ locale-gen en_US.UTF-8
# To check the list of installed locales:
# $ locale -a

#SORTING_LOCALE = 'fr_FR.UTF-8'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/user/profile'

# custom user model
AUTH_USER_MODEL = 'users.User'

# social auth
SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_LOGIN_ERROR_URL = '/settings/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/user/'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False


AUTHENTICATION_BACKENDS = (
    'social_core.backends.twitter.TwitterOAuth',
    #'social_core.backends.github.GithubOAuth2',
    #'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_TWITTER_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'moderation.profile.socialuser',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'moderation.profile.user',
    'moderation.profile.profile',
    'doctocnet.twitterinfo.show_profile',  # <--- set the path to the function
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'users.social_auth.add_email_if_not_exist',
)
MEDIA_ROOT = config('MEDIA_ROOT')
#MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'

# Redis & Celery
REDIS_HOST = config('REDIS_HOST', default='redis')
REDIS_PORT = config('REDIS_PORT', cast=str, default='6379')
CELERY_BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 3600,
    'fanout_prefix': True,
    'fanout_patterns': True} 
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_TASK_SOFT_TIME_LIMIT = config(
    'CELERY_TASK_SOFT_TIME_LIMIT',
    cast = int,
    default = 1500
)
CELERY_TASK_TIME_LIMIT = config(
    'CELERY_TASK_TIME_LIMIT',
    cast = int,
    default = 1750,
)
CELERY_LOG_FILE = config('CELERY_LOG_FILE')

CELERY_TASK_ROUTES = {
    'bot.tasks.handle_on_status': {'queue': 'retweet'},
    'conversation.tasks.handle_update_trees': {'queue': 'tree'},
}

ONCE = {
  'backend': 'celery_once.backends.Redis',
  'settings': {
    'url': CELERY_RESULT_BACKEND,
    'default_timeout': 60 * 60
  }
}

# CACHE
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://" + REDIS_HOST + ":" + REDIS_PORT + "/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
DISPLAY_CACHE = config('DISPLAY_CACHE', cast=int, default=60)

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ]
}

#Default time delta in hours for all functions related to scraping web tweets
SCRAPING_HOUR_DELTA = config('SCRAPING_HOUR_DELTA', cast=int)

# crispy_forms options
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# django-registration
ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window

MIGRATION_MODULES = {
    'sites': 'doctocnet.data_migrations.sites_migrations',
}

PAGINATION = config('PAGINATION', cast=int, default=1000)
DATA_UPLOAD_MAX_NUMBER_FIELDS = config('DATA_UPLOAD_MAX_NUMBER_FIELDS', cast=int, default=5000)

MODERATION = {
    "dev": False,
    "moderator": True
}

STATUS_DISPLAY_NUMBER = {
    'all': 10,
    'last': 10,
    'help': 10,
    'top': 10,
    'covid19': 10,
}

STATUS_DISPLAY_HOUR = {
    'all': 72,
    'last': 72,
    'help': 72,
    'top': 72,
    'covid19': 72,
}

#CORS_ORIGIN_ALLOW_ALL = True

# Messenger DM per task limit
MESSENGER_DM_LIMIT = 15

# django-meta

if DEBUG:
    if DEBUG_HTTPS:
        META_SITE_PROTOCOLE = "https"
    else:
        META_SITE_PROTOCOL = 'http'
else:
    META_SITE_PROTOCOL = 'https'

META_USE_SITES = True
META_USE_TWITTER_PROPERTIES = True

# Stripe
STRIPE_PUBLIC_KEY = config("STRIPE_PUBLIC_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_LIVE_MODE = False

EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=30, cast=int)
SERVER_EMAIL = config('SERVER_EMAIL', default='noreply@example.com')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@example.com')
ADMIN_FIRST_NAME = config('ADMIN_FIRST_NAME', default='admin')
ADMIN_LAST_NAME = config('ADMIN_LAST_NAME', default='admin')
ADMIN_NAME = " ".join([ADMIN_FIRST_NAME, ADMIN_LAST_NAME])
ADMIN_EMAIL_ADDRESS = config('ADMIN_EMAIL_ADDRESS', default='admin@example.com')
ADMINS=[
(ADMIN_NAME, ADMIN_EMAIL_ADDRESS),
]
MANAGERS=ADMINS
EMAIL_BACKEND=config('EMAIL_BACKEND')

# investment: this setting was used before community feature
#PROJECT_NAME = 'doctoctocbot'

# django-registration
REGISTRATION_SALT = config('REGISTRATION_SALT')
ACCOUNT_ACTIVATION_DAYS = config('ACCOUNT_ACTIVATION_DAYS', default=1, cast=int)

import mimetypes
mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("text/css", ".scss", True)

# main bot Twitter account
TWITTER_CONSUMER_KEY = config('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = config('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN = config('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = config('TWITTER_ACCESS_TOKEN_SECRET')
BOT_IMAGES_PATH = config('BOT_IMAGES_PATH')
NUMBER_OF_RT = 20
TWEET_LANGUAGE = ""
TWEET_LENGTH = 280

# APP
TWITTER_APP_CONSUMER_KEY = config('TWITTER_APP_CONSUMER_KEY')
TWITTER_APP_CONSUMER_SECRET = config('TWITTER_APP_CONSUMER_SECRET')

# Twitter key (social-auth-app-django)
SOCIAL_AUTH_TWITTER_KEY = config('TWITTER_CONSUMER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = config('TWITTER_CONSUMER_SECRET')

# gpgcontact
GNUPGHOME = config('GNUPGHOME')
GNUPG_PUBLIC_KEYS = config('GNUPG_PUBLIC_KEYS', cast=Csv())

PROFILE_TIMEDELTA_DAYS = config('PROFILE_TIMEDELTA_DAYS', default=0, cast=int)
FOLLOWER_TIMEDELTA_HOUR = config('FOLLOWER_TIMEDELTA_HOUR', default=24, cast=int)
FRIEND_TIMEDELTA_HOUR = config('FRIEND_TIMEDELTA_HOUR', default=24, cast=int)
TRANSLATION_OVERRIDE='fr'

# Constants
# url used to fetch a status from its status id
TWITTER_STATUS_URL='https://twitter.com/i/web/status/{id}'

# Discourse
DISCOURSE_SSO_SECRET = config('DISCOURSE_SSO_SECRET')
DISCOURSE_BASE_URL = config('DISCOURSE_BASE_URL')

# First community
COMMUNITY_NAME = config('COMMUNITY_NAME')
COMMUNITY_ACCOUNT_USERNAME = config('COMMUNITY_ACCOUNT_USERNAME')
COMMUNITY_ACCOUNT_USERID =  config('COMMUNITY_ACCOUNT_USERID', cast=int)
COMMUNITY_HASHTAG_LIST = config('COMMUNITY_HASHTAG_LIST', cast=Csv())
COMMUNITY_MEMBERSHIP_LIST = config('COMMUNITY_MEMBERSHIP_LIST', cast=Csv())
COMMUNITY_SITE_ID = config('COMMUNITY_SITE_ID', cast=int)
COMMUNITY_SITE_NAME = config('COMMUNITY_SITE_NAME')
COMMUNITY_SITE_DOMAIN = config('COMMUNITY_SITE_DOMAIN') 
COMMUNITY_CROWDFUNDING = config('COMMUNITY_CROWDFUNDING')

# django-taggit
TAGGIT_CASE_INSENSITIVE = True

if DEBUG:
    # CORS
    CORS_ORIGIN_ALLOW_ALL = config('CORS_ORIGIN_ALLOW_ALL', default=False, cast=bool)
    CORS_ORIGIN_WHITELIST = config('CORS_ORIGIN_WHITELIST', cast=Csv())
    

# Copper (name of Silver billing app inside our project)
SILVER_EXTRA = config('SILVER_EXTRA', default="") # "Tax exempt due to XXX"
SILVER_SALES_TAX_PERCENT = config('SILVER_SALES_TAX_PERCENT', cast=int, default=0) # 24
SILVER_SALES_TAX_NAME = config('SILVER_SALES_TAX_NAME', default="") # "VAT"
SILVER_SALES_TAX_NUMBER = config('SILVER_SALES_TAX_NUMBER', default="") # "1234567890"
# Copper 
SILVER_TOKEN = config('SILVER_TOKEN')
SILVER_URL = config('SILVER_URL')

PAYMENT_PROCESSORS = {}
SILVER_AUTOMATICALLY_CREATE_TRANSACTIONS = False
SILVER_DOCUMENT_PREFIX = config('SILVER_DOCUMENT_PREFIX')
SILVER_DOCUMENT_STORAGE = None
SILVER_IS_LOCAL = config('SILVER_IS_LOCAL', default=True, cast=bool)

DISCOURSE_HOSTNAME = config('DISCOURSE_HOSTNAME')
DISCOURSE_PROTOCOL = config('DISCOURSE_PROTOCOL', default='https')
DISCOURSE_IP_CACHE_TTL = config('DISCOURSE_IP_CACHE_TTL', cast=int, default=3600)
DISCOURSE_IP_CACHE_KEY = config('DISCOURSE_IP_CACHE_KEY', default="discourse_ip")
DISCOURSE_WEBHOOK_SECRET = config('DISCOURSE_WEBHOOK_SECRET')
DISCOURSE_API_KEY_SYSTEM = config('DISCOURSE_API_KEY_SYSTEM')

# Invite
INVITATIONS_SIGNUP_REDIRECT = 'register-invite-email'
INVITATIONS_INVITATION_MODEL = 'invite.CategoryInvitation'
INVITATION_USE_SESSION_KEY = config(
    'INVITATION_USE_SESSION_KEY',
    default=True,
    cast=bool
)
INVITATION_SESSION_KEY = config(
    'INVITATION_SESSION_KEY',
    default='invitation_session_key'
)

THIS_SOCIAL_MEDIA =  config('THIS_SOCIAL_MEDIA', default='this_social_media')

COVID19_CATEGORIES = config(
    'COVID19_CATEGORIES',
    cast=Csv(),
    default='physician, midwife, pharmacist'
)
DATA_UPLOAD_MAX_NUMBER_FIELDS = config(
    'DATA_UPLOAD_MAX_NUMBER_FIELDS',
    cast=int,
    default=1000
) # higher than the count of fields

# Time in seconds between two Friends API requests
API_FRIENDS_PERIOD = config('API_FRIENDS_PERIOD', cast=int, default=70)
API_FOLLOWERS_PERIOD = config('API_FOLLOWERS_PERIOD', cast=int, default=70)

# default for verification_threshold_follower (int)
VERIFICATION_THRESHOLD_FOLLOWER = config(
    'VERIFICATION_THRESHOLD_FOLLOWER',
    cast=int,
    default=1
)

#Constance
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_DATABASE_CACHE_BACKEND = 'default'
CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True

CONSTANCE_CONFIG = {
    'email_verification': (
        "Verify your identity by entering the email address associated with "
        "your Twitter account",
        "Document source text to identify email verification page"
    ),
    "follower_requests_url": (
        "https://mobile.twitter.com/follower_requests?commit=Follower+requests",
        "URL of the page to accept follower requests"
    ),
    "selenium_firefox_headers": (
        "",
        "Firefox headers sent by Selenium"
    ),
}