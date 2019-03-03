from pathlib import Path
from decouple import AutoConfig
from dj_database_url import parse as db_url

from .base import *

CONFIG_DIR = Path("/home/elkcloner/.doctocnet/staging")
config = AutoConfig(search_path = CONFIG_DIR)

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS += ['staging.doctoctoc.net']

INSTALLED_APPS += [
    'status',
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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
# Static files (CSS, JavaScript, Images)                                        
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "doctocnet/static/"),
        ]

STATIC_ROOT='/var/cache/doctocnet/static/'
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

# Braintree
BRAINTREE_PRODUCTION = False  # We'll need this later to switch between the sandbox and live account
BRAINTREE_MERCHANT_ID = config('BRAINTREE_MERCHANT_ID', default='')
BRAINTREE_PUBLIC_KEY = config('BRAINTREE_PUBLIC_KEY', default='')
BRAINTREE_PRIVATE_KEY = config('BRAINTREE_PRIVATE_KEY', default='')