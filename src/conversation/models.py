from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.utils import DatabaseError
from django.utils.safestring import mark_safe
from django.conf import settings
import logging
from mptt.models import MPTTModel, TreeForeignKey
from common.twitter import status_url_from_id
from taggit.managers import TaggableManager
from taggit.models import CommonGenericTaggedItemBase, TaggedItemBase
from django.utils.translation import ugettext_lazy as _
from versions.models import Versionable

logger = logging.getLogger(__name__)


class GenericBigIntTaggedItem(CommonGenericTaggedItemBase, TaggedItemBase):
    object_id = models.BigIntegerField(verbose_name=_('Object id'), db_index=True)


class Hashtag(models.Model):
    hashtag = models.CharField(max_length=101, unique=True)
    
    def __str__(self):
        return self.hashtag

    @staticmethod
    def has_read_permission(self):
        return True

    def has_write_permission(self):
        return False
    
    def has_update_permission(self):
        return False


class Tweetdj(models.Model):
    statusid = models.BigIntegerField(unique=True, primary_key=True)
    userid = models.BigIntegerField()
    socialuser = models.ForeignKey(
        'moderation.SocialUser',
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="tweets"
    )
    json = JSONField()
    created_at = models.DateTimeField()
    reply = models.PositiveIntegerField(null=True)
    like = models.PositiveIntegerField(null=True)
    retweet = models.PositiveIntegerField(null=True)
    parentid = models.BigIntegerField(null=True)
    quotedstatus = models.NullBooleanField(
        default=None,
        help_text="Is quoted_status",
        verbose_name="Quote",
    )
    retweetedstatus = models.NullBooleanField(
        default=None,
        help_text="Has retweeted_status",
        verbose_name="RT",
    )
    deleted = models.NullBooleanField(
        default=None,
        help_text="Has this tweet been deleted?",
        verbose_name="Del",
    )
    hashtag = models.ManyToManyField(
        Hashtag,
        blank=True,
    )
    tags = TaggableManager(through=GenericBigIntTaggedItem)
    retweeted_by = models.ManyToManyField(
        "moderation.SocialUser",
        blank=True,
    )
    
    
    class Meta:
        get_latest_by = "statusid"
        ordering = ('-statusid',)

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
        url = status_url_from_id(self.statusid)
        return mark_safe(f'<a href="{url}">🐦</a>')
    
    status_url_tag.short_description = "Link"

    def status_text_tag(self):
        status = self.json
        if not isinstance(status, dict):
            return
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
    def getstatustext(cls, statusid: int) -> str:
        if not statusid:
            return ""
        try:
            status_mi = cls.objects.get(statusid = statusid)
        except cls.DoesNotExist:
            return ""
        status = status_mi.json
        if 'full_text' in status: 
            return status.get("full_text") or ""
        elif 'text' in status:
            return status.get("text") or ""
        else:
            return ""

class Treedj(MPTTModel):
    statusid = models.BigIntegerField(unique=True)
    #tweet = models.OneToOneField(Tweetdj, on_delete=models.CASCADE)
    parent = TreeForeignKey('self',
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True,
                            related_name='children')

    def __str__(self):
        return settings.TWITTER_STATUS_URL.format(id=self.statusid)

    def status_url_tag(self):
        url = status_url_from_id(self.statusid)
        return mark_safe(f'<a href="{url}">🐦</a>')

    status_url_tag.short_description = "Tweet"

    def status_text_tag(self):
        try:
            status = Tweetdj.objects.get(statusid=self.statusid).json
        except Tweetdj.DoesNotExist:
            return
        
        if 'full_text' in status:  
            status_str = status.get("full_text")
        elif 'text' in status:
            status_str = status.get("text")
        else:
            status_str = ""
            
        return status_str
    
    status_text_tag.short_description = "Text"

    class MPTTMeta:
        order_insertion_by = ['statusid']
        order_by = ['-statusid']
        
def create_tree(statusid):
    try:
        return Treedj.objects.create(statusid=statusid)
    except DatabaseError as e:
        logger.error(str(e))

def create_leaf(statusid, parentid):
    try:
        parent_mi = Treedj.objects.get(statusid=parentid)
    except Treedj.DoesNotExist:
        return None
    try:
        leaf = Treedj.objects.create(statusid=statusid, parent=parent_mi)
    except DatabaseError as e:
        leaf = None
        logger.error(str(e))
    return leaf


class Retweeted(Versionable):
    status = models.BigIntegerField()
    retweet = models.BigIntegerField()
    account = models.ForeignKey(
        "bot.Account",
        on_delete=models.CASCADE,
    )