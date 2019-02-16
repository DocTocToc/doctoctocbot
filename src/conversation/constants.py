"""
Constants
"""
from django.conf import settings

if hasattr(settings, 'SCRAPING_HOUR_DELTA'):
    HOURS = settings.SCRAPING_HOUR_DELTA
else:
    HOURS = 24
    
TWEETDJ_PAGINATION = 1000