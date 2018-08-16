from django.db import models
from django.contrib.postgres.fields import JSONField
from mptt.models import MPTTModel, TreeForeignKey

class Tweetdj(models.Model):
    statusid = models.BigIntegerField(unique=True, primary_key=True)
    userid = models.BigIntegerField()
    json = JSONField()
    datetime = models.DateTimeField()
    reply = models.PositiveIntegerField()
    like = models.PositiveIntegerField()
    retweet = models.PositiveIntegerField()

    def __str__(self):
        return self.statusid

class Treedj(MPTTModel):
    statusid = models.BigIntegerField(unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,
    blank=True, related_name='children')

    def __str__(self):
        return "https://twitter.com/statuses/" +  str(self.statusid)

    class MPTTMeta:
        order_insertion_by = ['statusid']
