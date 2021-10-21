from doctocnet.settings import *

SITE_ID = config('SITE_ID_6', cast=int, default=6)
ROOT_URLCONF = config('ROOT_URLCONF_6', default='doctocnet.urls')