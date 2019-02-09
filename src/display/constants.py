"""
Constants
"""
from django.conf import settings

if hasattr(settings, 'SCRAPING_HOUR_DELTA'):
    HOURS = settings.SCRAPING_HOUR_DELTA
else:
    HOURS = 24
    
DISPLAY_CACHE = 60