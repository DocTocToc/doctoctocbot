from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db import IntegrityError, transaction

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