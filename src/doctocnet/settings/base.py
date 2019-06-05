"""
Django settings for doctocnet project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

from django.conf.global_settings import AUTH_USER_MODEL
from django.utils.translation import gettext_lazy as _
import os
import sys

from decouple import AutoConfig
from pathlib import Path


CONFIG_DIR = Path("/home/elkcloner/.doctocnet/base")
config = AutoConfig(search_path = CONFIG_DIR)

#sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/


ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.1.102']

SITE_ID = 1

# Application definition

INSTALLED_APPS = [
    'users',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
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
]

MIDDLEWARE = [
    # CORS
    #'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'doctocnet.urls'

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'django.template.context_processors.media',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'doctocnet.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': 'doctocnet',
#        'HOST': 'localhost',
#        'USER': 'doctocnet',
#        'PASSWORD': 'doctocnet',
#    }
#}


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
#    ('en', _('English')),

]

# use this locale to sort localized strings, default to 'en_US.UTF-8'
# you have to generate the locales you will use on your GNU/Linux server:
# $ locale-gen fr_FR.UTF-8
# $ locale-gen en_US.UTF-8
# To check the list of installed locales:
# $ locale -a

SORTING_LOCALE = 'fr_FR.UTF-8'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True




LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/user/'

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
)
#MEDIA_ROOT = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'

# Redis & Celery
REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 3600,
    'fanout_prefix': True,
    'fanout_patterns': True} 
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_TASK_SOFT_TIME_LIMIT = 1010
CELERY_TASK_TIME_LIMIT = 1020


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            #'PASSWORD': 'a_better_password_please',
        }
    }
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

#Default time delta in hours for all functions related to scraping web tweets
SCRAPING_HOUR_DELTA = 24

# crispy_forms options
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# django-registration
ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window

MIGRATION_MODULES = {
    'sites': 'doctocnet.data_migrations.sites_migrations',
}

PAGINATION = 1000

MODERATION = {
    "dev": False,
    "moderator": True
}

STATUS_DISPLAY_NUMBER = {
    'all': 10,
    'last': 10,
    'help': 10,
    'top': 10
}

STATUS_DISPLAY_HOUR = {
    'all': 48,
    'last': 48,
    'help': 48,
    'top': 48
}

BEAT_PERIOD = {
    'record_timeline': 60.0,
    'scrape_web_timeline': 120.0,
    'normalize': 600.0,
    'poll_dm': 600.0,
    'poll_moderation_dm': 600.0,
    'update_trees': 300.0,
    'poll_lists_members': 900.0,
}

LISTS_BACKUP_PATH = ""

MODERATION_AUTHORIZED_CATEGORIES = ['physician', 'midwife',]

# Path on disk where images are saved
BOT_IMAGES_PATH = ""

#CORS_ORIGIN_ALLOW_ALL = True

# Messenger DM per task limit
MESSENGER_DM_LIMIT = 15