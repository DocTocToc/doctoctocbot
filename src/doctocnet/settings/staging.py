from pathlib import Path
from decouple import AutoConfig, Csv
from dj_database_url import parse as db_url

from .base import *

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

# Braintree
BRAINTREE_PRODUCTION = False  # We'll need this later to switch between the sandbox and live account
BRAINTREE_MERCHANT_ID = config('BRAINTREE_MERCHANT_ID', default='')
BRAINTREE_PUBLIC_KEY = config('BRAINTREE_PUBLIC_KEY', default='')
BRAINTREE_PRIVATE_KEY = config('BRAINTREE_PRIVATE_KEY', default='')

STRIPE_PUBLIC_KEY = config("STRIPE_TEST_PUBLIC_KEY", default="")
STRIPE_SECRET_KEY = config("STRIPE_TEST_SECRET_KEY", default="")
STRIPE_LIVE_MODE = False

# BOT settings
# Path on disk where images are saved
BOT_IMAGES_PATH = config('BOT_IMAGES_PATH', default = "~/Pictures")
KEYWORD_TRACK_LIST = ["#doctoctoc", "#docstoctoctest"]
KEYWORD_RETWEET_LIST = ["#doctoctoc",]

# gpgcontact
GNUPGHOME = config('GNUPGHOME')
GNUPG_PUBLIC_KEYS = config('GNUPG_PUBLIC_KEYS', cast=Csv())