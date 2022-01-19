from doctocnet.settings import *

SITE_ID = config('SITE_ID_7', cast=int, default=6)
ROOT_URLCONF = config('ROOT_URLCONF_7', default='doctocnet.urls')