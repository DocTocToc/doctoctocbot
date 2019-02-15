from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.utils import DatabaseError
from django.utils.safestring import mark_safe
import logging

from mptt.models import MPTTModel, TreeForeignKey


logger = logging.getLogger(__name__)

class Tweetdj(models.Model):
    statusid = models.BigIntegerField(unique=True, primary_key=True)
    userid = models.BigIntegerField()
    json = JSONField()
    created_at = models.DateTimeField()
    reply = models.PositiveIntegerField(null=True)
    like = models.PositiveIntegerField(null=True)
    retweet = models.PositiveIntegerField(null=True)
    parentid = models.BigIntegerField(null=True)
    hashtag0 = models.NullBooleanField(default=None, help_text="doctoctoc(test)")
    hashtag1 = models.NullBooleanField(default=None, help_text="docstoctoc(test)")
    quotedstatus = models.NullBooleanField(default=None, help_text="Is quoted_status")
    retweetedstatus = models.NullBooleanField(default=None, help_text="Is retweeted_status")
    deleted = models.NullBooleanField(default=None, help_text="Has this tweet been deleted?")
    
    class Meta:
        get_latest_by = "-statusid"

    def __str__(self):
        return str(self.statusid)
    
    def convertDatetimeToString(self):
        import datetime
        DATE_FORMAT = "%Y-%m-%d" 
        TIME_FORMAT = "%H:%M:%S"

        if isinstance(self, datetime.date):
            return self.strftime(DATE_FORMAT)
        elif isinstance(self, datetime.time):
            return self.strftime(TIME_FORMAT)
        elif isinstance(self, datetime.datetime):
            return self.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT))
    
    def status_url_tag(self):
        return mark_safe('<a href="https://twitter.com/statuses/%s">Link</a>' % (self.statusid))
    
    status_url_tag.short_description = "Link"

    def status_text_tag(self):
        status = self.json
        if 'full_text' in status:  
            status_str = status.get("full_text")
        elif 'text' in status:
            status_str = status.get("text")
        else:
            status_str = ""
            
        return status_str
    
    status_text_tag.short_description = "Text"
    
    def screen_name_tag(self):
        status = self.json
        if "user" in status:  
            if "screen_name" in status["user"]:
                screen_name = status["user"]["screen_name"]
        else:
            screen_name = ""
            
        return screen_name
    
    screen_name_tag.short_description = "Screen name"    

    #def save(self, *args, **kwargs):
    #    if self.parentid is not None:
    #        parentNode, _ = Treedj.objects.get_or_create(statusid=self.parentid)
    #        try:
    #            Treedj.objects.create(statusid = self.statusid, parent = parentNode)
    #        except IntegrityError:
    #            continue
    #    super(Tweetdj, self).save(*args, **kwargs)

    @classmethod
    def getstatustext(cls, id) -> str:
        try:
            status_mi = cls.objects.get(statusid = id)
        except cls.DoesNotExist:
            return None
        status = status_mi.json
        if 'full_text' in status:  
            status_str = status.get("full_text")
        elif 'text' in status:
            status_str = status.get("text")
        else:
            status_str = ""
            
        return status_str

class Treedj(MPTTModel):
    statusid = models.BigIntegerField(unique=True)
    #tweet = models.OneToOneField(Tweetdj, on_delete=models.CASCADE)
    parent = TreeForeignKey('self',
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True,
                            related_name='children')

    def __str__(self):
        return "https://twitter.com/statuses/" +  str(self.statusid)
    
    def status_url_tag(self):
        return mark_safe('<a href="https://twitter.com/statuses/%s">Link</a>' % (self.statusid))

    class MPTTMeta:
        order_insertion_by = ['statusid']
        order_by = ['statusid']
        
def create_tree(statusid):
    try:
        Treedj.objects.create(statusid=statusid)
    except DatabaseError as e:
        logger.error(str(e))

def create_leaf(statusid, parentid):
    try:
        parent_mi = Treedj.objects.get(statusid=parentid)
    except Treedj.DoesNotExist:
        return None
    leaf = None
    try:
        leaf = Treedj.objects.create(statusid=statusid, parent=parent_mi)
    except DatabaseError as e:
        logger.error(str(e))
    return leaf