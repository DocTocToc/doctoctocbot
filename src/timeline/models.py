from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import IntegrityError, transaction
from django.db import models
import logging


logger = logging.getLogger(__name__)

class Status(models.Model):
    statusid = models.BigIntegerField(unique=True, primary_key=True)
    json = JSONField()
    
    class Meta:
        ordering = ["-statusid"]
        get_latest_by = "-statusid"
    

def add_status_tl(status):
    """
    Add a tweepy status object to the timeline table.
    """
    try:
        with transaction.atomic():
            status_mi = Status(statusid=status.id,
                               json=status._json)
            status_mi.save()
    except IntegrityError:
        pass
    
def last_tl_statusid_lst(hourdelta=None):
    """Return tweets of interest (that are not replies) from the timeline
    created in the last hourdelta hours
    """
    from datetime import datetime, timedelta
    from bot.lib.datetime import get_datetime
    
    if hourdelta is None:
        hourdelta = settings.SCRAPING_HOUR_DELTA
    
    logger.debug(f"hourdelta: {hourdelta}")
    since = datetime.utcnow() - timedelta(hours=hourdelta)
    logger.debug(f"since: {hourdelta}")
    sid_lst = []
    for status in Status.objects.all().filter(json__contains={'in_reply_to_status_id': None}):
        dt = get_datetime(status.json)
        logger.debug(f"dt: {dt}")
        if dt > since:
            sid_lst.append(status.statusid)
    return sid_lst
        
    