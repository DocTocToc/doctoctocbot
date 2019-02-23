from datetime import datetime, timedelta
from bot.lib.datetime import get_datetime
from bot.lib.snowflake import snowflake2utc

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.utils.safestring import mark_safe
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
        verbose_name_plural = "statuses"
    
    def status_url_tag(self):
        return mark_safe('<a href="https://twitter.com/statuses/%s">Link</a>' % (self.statusid))

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
    if hourdelta is None:
        hourdelta = settings.SCRAPING_HOUR_DELTA
    
    since = datetime.utcnow() - timedelta(hours=hourdelta)
    sid_lst = []
    for status in Status.objects.all().filter(json__contains={'in_reply_to_status_id': None}):
        dt = get_datetime(status.json)
        logger.debug(f"dt: {dt}")
        if dt > since:
            sid_lst.append(status.statusid)
    return sid_lst
        
def last_retweeted_statusid_lst(hourdelta=None):
    """Return a list of statusid of tweets that were retweeted by the bot and
    that were created less than hourdelta hours ago.
    """
    if hourdelta is None:
        hourdelta = settings.SCRAPING_HOUR_DELTA
    
    since = datetime.utcnow() - timedelta(hours=hourdelta)
    since_ts_ms = datetime.timestamp(since)*1000
    #Status.objects.all().filter(json__contains={'retweeted_satus'})
    #Status.objects.raw("SELECT statusid FROM timeline_status WHERE (((json->>'id')::bigint) >> 22) + 1288834974657 > 1548679041866")
    rqs = Status.objects.raw(
        "SELECT "
        "statusid "
        "FROM "
        "timeline_status "
        "WHERE "
        "(((json->'retweeted_status'->>'id')::bigint) >> 22) + 1288834974657 > %s",
        [since_ts_ms]
    )
    return [row.json['retweeted_status']['id'] for row in rqs]
