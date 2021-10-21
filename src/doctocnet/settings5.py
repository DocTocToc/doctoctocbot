from doctocnet.settings import *

SITE_ID = config('SITE_ID_5', cast=int, default=5)
ROOT_URLCONF = config('ROOT_URLCONF_5', default='doctocnet.urls')