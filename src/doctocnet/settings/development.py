from decouple import AutoConfig, Csv
from dj_database_url import parse as db_url
from pathlib import Path

from .base import *


CONFIG_DIR = Path("/home/elkcloner/.doctocnet/development")
config = AutoConfig(search_path = CONFIG_DIR)

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)
#INTERNAL_IPS = ['127.0.0.1']

ALLOWED_HOSTS = ['tunnel.doctoctoc.net', 'localhost', '127.0.0.1', '[::1]']

INSTALLED_APPS += [
    #'debug_toolbar',
    'status',
    'django_extensions',
    'gpgcontact',
    #'djstripe',
]

MIDDLEWARE += [
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
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

STATICFILES_DIRS = [
        ]

STATIC_ROOT = config('STATIC_ROOT')
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
PAYPAL_PRIVATE_CERT = '/home/elkcloner/doctoctocbot/paypal/sandbox/my-prvkey.pem'
PAYPAL_PUBLIC_CERT = '/home/elkcloner/doctoctocbot/paypal/sandbox/my-prvkey.pem'
PAYPAL_CERT = '/home/elkcloner/doctoctocbot/paypal/sandbox/paypal_cert.pem'
PAYPAL_CERT_ID = 'KHSHGAPVMJ42U'

# Braintree
#BRAINTREE_PRODUCTION = False  # We'll need this later to switch between the sandbox and live account
#BRAINTREE_MERCHANT_ID = config('BRAINTREE_MERCHANT_ID')
#BRAINTREE_PUBLIC_KEY = config('BRAINTREE_PUBLIC_KEY')
#BRAINTREE_PRIVATE_KEY = config('BRAINTREE_PRIVATE_KEY')

# Stripe
#STRIPE_LIVE_PUBLIC_KEY = config("STRIPE_LIVE_PUBLIC_KEY")
#STRIPE_LIVE_SECRET_KEY = config("STRIPE_LIVE_SECRET_KEY")
STRIPE_PUBLIC_KEY = config("STRIPE_TEST_PUBLIC_KEY")
STRIPE_SECRET_KEY = config("STRIPE_TEST_SECRET_KEY")
DJSTRIPE_WEBHOOK_SECRET = config("DJSTRIPE_WEBHOOK_SECRET")
STRIPE_LIVE_MODE = False

# mail
#EMAIL_HOST = config('EMAIL_HOST', default='localhost')
#EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
#EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
#EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
#EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=True, cast=bool)
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
EMAIL_BACKEND='django_sendmail_backend.backends.EmailBackend'

# investment
PROJECT_NAME = 'doctoctocbot'

BEAT_PERIOD = {
    'record_timeline': 120.0,
    'scrape_web_timeline': 120.0,
    'normalize': 600.0,
    'poll_dm': 180.0,
    'poll_moderation_dm': 120.0,
    'update_trees': 300.0,
}

LISTS_BACKUP_PATH = config('LISTS_BACKUP_PATH', default='/tmp')

# django-registration
REGISTRATION_SALT = 'YYrwXggvsquEMiZ45BA3CyAtxthUdbR45PZ'
ACCOUNT_ACTIVATION_DAYS = 42

import mimetypes
mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("text/css", ".scss", True)

# Path on disk where images are saved
BOT_IMAGES_PATH = config('BOT_IMAGES_PATH', default = "~/Pictures")

# gpgcontact
GNUPGHOME = config('GNUPGHOME')
GNUPG_PUBLIC_KEYS = config('GNUPG_PUBLIC_KEYS', cast=Csv())