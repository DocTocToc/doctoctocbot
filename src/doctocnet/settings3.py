from doctocnet.settings import *

SITE_ID = config('SITE_ID_3', cast=int, default=3)
ROOT_URLCONF = config('ROOT_URLCONF_3', default='doctocnet.urls')