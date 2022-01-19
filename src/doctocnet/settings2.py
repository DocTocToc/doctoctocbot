from doctocnet.settings import *

SITE_ID = config('SITE_ID_2', cast=int, default=2)
ROOT_URLCONF = config('ROOT_URLCONF_2', default='doctocnet.urls')
