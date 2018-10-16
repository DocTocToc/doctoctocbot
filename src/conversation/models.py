from django.db import models
from django.contrib.postgres.fields import JSONField
from mptt.models import MPTTModel, TreeForeignKey

class Tweetdj(models.Model):
    statusid = models.BigIntegerField(unique=True, primary_key=True)
    userid = models.BigIntegerField()
    json = JSONField()
    created_at = models.DateTimeField()
    reply = models.PositiveIntegerField()
    like = models.PositiveIntegerField()
    retweet = models.PositiveIntegerField()
    parentid = models.BigIntegerField(null=True)

    def __str__(self):
        return str(self.statusid)

    def save(self, *args, **kwargs):
        if self.parentid is not None:
            parentNode = Treedj.objects.get(statusid=self.parentid)
            treeNode = Treedj(statusid = self.statusid, parent = parentNode)
            treeNode.save()
        super(Tweetdj, self).save(*args, **kwargs)

class Treedj(MPTTModel):
    statusid = models.BigIntegerField(unique=True)
    #tweet = models.OneToOneField(Tweetdj, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True,
    blank=True, related_name='children')

    def __str__(self):
        return "https://twitter.com/statuses/" +  str(self.statusid)

    class MPTTMeta:
        order_insertion_by = ['statusid']