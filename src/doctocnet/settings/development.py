from decouple import AutoConfig
from dj_database_url import parse as db_url
from pathlib import Path

from .base import *


CONFIG_DIR = Path("/home/elkcloner/.doctocnet/development")
config = AutoConfig(search_path = CONFIG_DIR)

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

INTERNAL_IPS = ['127.0.0.1']

INSTALLED_APPS += [
    'debug_toolbar',
    'status',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

DATABASES = {
    'default': config(
        'DATABASE_URL',
        #default='',
        cast=db_url
    ),
    'status': config(
        'DATABASE_URL_PRODSTATUS',
        cast=db_url
    ),
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
# Static files (CSS, JavaScript, Images)                                        
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "doctocnet/static/"),
        #'/var/www/static/',
        ]

# STATIC_ROOT = ''
STATIC_URL = '/static/'

# Postgres
POSTGRESQL = {
    "username":"doctoctoctest",
    "password":"doctoctoctest",
    "host":"127.0.0.1",
    "port":"5432",
    "database":"status"
}

# django-paypal
PAYPAL_RECEIVER_EMAIL = 'jerome-facilitator@jerome.cc'
 
PAYPAL_TEST = True

# Braintree
BRAINTREE_PRODUCTION = False  # We'll need this later to switch between the sandbox and live account
BRAINTREE_MERCHANT_ID = config('BRAINTREE_MERCHANT_ID')
BRAINTREE_PUBLIC_KEY = config('BRAINTREE_PUBLIC_KEY')
BRAINTREE_PRIVATE_KEY = config('BRAINTREE_PRIVATE_KEY')

# mail
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=True, cast=bool)

# investment
PROJECT_NAME = 'doctoctocbot'