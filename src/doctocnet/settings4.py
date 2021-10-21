from doctocnet.settings import *

SITE_ID = config('SITE_ID_4', cast=int, default=4)
ROOT_URLCONF = config('ROOT_URLCONF_4', default='doctocnet.urls')