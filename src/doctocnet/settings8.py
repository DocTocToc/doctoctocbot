from doctocnet.settings import *

SITE_ID = config('SITE_ID_8', cast=int, default=8)
ROOT_URLCONF = config('ROOT_URLCONF_8', default='doctocnet.urls')