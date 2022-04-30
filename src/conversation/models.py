from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.utils import DatabaseError, IntegrityError
from django.utils.safestring import mark_safe
from django.conf import settings
import logging
from mptt.models import MPTTModel, TreeForeignKey
from common.twitter import status_url_from_id
from taggit.managers import TaggableManager
from taggit.models import CommonGenericTaggedItemBase, TaggedItemBase
from django.utils.translation import ugettext_lazy as _
from versions.models import Versionable
from fuzzycount import FuzzyCountManager
from versions.models import Versionable
from django.db.models import Q
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.urls import reverse

logger = logging.getLogger(__name__)


class GenericBigIntTaggedItem(CommonGenericTaggedItemBase, TaggedItemBase):
    object_id = models.BigIntegerField(verbose_name=_('Object id'), db_index=True)


class HashtagManager(models.Manager):
    def get_by_natural_key(self, hashtag):
        return self.get(hashtag=hashtag)


class Hashtag(models.Model):
    hashtag = models.CharField(max_length=101, unique=True)
    
    objects = HashtagManager()

    def natural_key(self):
        return (self.hashtag,)

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
    statusid = models.BigIntegerField(primary_key=True)
    userid = models.BigIntegerField()
    socialuser = models.ForeignKey(
        'moderation.SocialUser',
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="tweets"
    )
    json = models.JSONField(
        null=True
    )
    created_at = models.DateTimeField(null=True)
    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True
    )
    reply = models.PositiveIntegerField(null=True)
    like = models.PositiveIntegerField(null=True)
    retweet = models.PositiveIntegerField(null=True)
    parentid = models.BigIntegerField(null=True)
    retweetedstatus = models.BooleanField(
        default=None,
        help_text="Has retweeted_status",
        verbose_name="RT",
        null=True,
    )
    quotedstatus = models.BooleanField(
        default=None,
        help_text="Has quoted_status",
        verbose_name="QT",
        null=True,
    )
    deleted = models.BooleanField(
        default=None,
        help_text="Has this tweet been deleted?",
        verbose_name="Del",
        null=True,
    )
    hashtag = models.ManyToManyField(
        Hashtag,
        blank=True,
    )
    tags = TaggableManager(through=GenericBigIntTaggedItem)
    retweeted_by = models.ManyToManyField(
        "moderation.SocialUser",
        related_name = "retweets",
        blank=True,
    )
    quoted_by = models.ManyToManyField(
        "moderation.SocialUser",
        related_name = "quotes",
        blank=True,
    )
    status_text = SearchVectorField(null=True)

    objects = FuzzyCountManager()

    class Meta:
        get_latest_by = "statusid"
        ordering = ('-statusid',)
        indexes = [
            models.Index(fields=['userid'], name='userid_idx'),
            GinIndex(fields=["status_text"]),
        ]

    def __str__(self):
        try:
            txt = self.json["full_text"]
        except (AttributeError, TypeError) as e:
            logger.error(f'Tweetdj {e} {self.statusid=}')
            txt = None
        except KeyError:
            try:
                txt = self.json["text"]
            except KeyError:
                txt = None
        return f"{self.statusid} {txt}"

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

    def admin_link(self):
        return mark_safe(
            '<a href="{link}">💽</a>'.format(
                link = reverse(
                    "admin:conversation_tweetdj_change",
                    args=(self.pk,)
                )
            )
        )

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

    class MPTTMeta:
        order_insertion_by = ['statusid']

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

        
def create_tree(statusid):
    try:
        return Treedj.objects.create(statusid=statusid)
    except (DatabaseError, IntegrityError) as e:
        logger.debug(str(e))

def create_leaf(statusid, parentid):
    try:
        parent_mi = Treedj.objects.get(statusid=parentid)
    except Treedj.DoesNotExist:
        return
    try:
        return Treedj.objects.get(statusid=statusid, parent=parent_mi)
    except Treedj.DoesNotExist:
        try:
            return Treedj.objects.create(statusid=statusid, parent=parent_mi)
        except (DatabaseError, IntegrityError) as e:
            logger.debug(str(e))

class Retweeted(Versionable):
    status = models.BigIntegerField()
    retweet = models.BigIntegerField()
    account = models.ForeignKey(
        "bot.Account",
        on_delete=models.CASCADE,
    )

class TwitterUserTimeline(models.Model):
    """ Trace first full retrieval of a user's timeline through API 1.1
    and record last status id each time this endpoint is called.
    Speed up subsequent retrievals by limiting them with "since
    status id".
    """
    userid = models.BigIntegerField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    last_api_call = models.DateTimeField(
        blank=True,
        null=True,
    )
    statusid_updated_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    statusid = models.BigIntegerField(
        null=True,
        blank=True,
        help_text = "Status id of the most recent status retrieved"
    )


class TwitterLanguageIdentifier(models.Model):
    tag = models.CharField(
        max_length=35,
        unique=True
    )
    language = models.CharField(
        max_length=255,
        unique=True
    )
    postgresql_dictionary = models.ForeignKey(
        "conversation.PostgresqlDictionary",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )


    class Meta:
        ordering = ['language']
        unique_together = [['tag', 'language']]


    def __str__(self):
        return '%s %s' % (self.language, self.tag)


class PostgresqlDictionary(models.Model):
    cfgname = models.CharField(
        max_length=255,
        unique=True
    )

    class Meta:
        verbose_name_plural = "Postgresql dictionaries"

    def __str__(self):
        return '%s %s' % (self.id, self.cfgname)


class DoNotRetweetStatus(Versionable):
    status = models.ForeignKey(
        Tweetdj,
        on_delete=models.PROTECT,
        related_name='donotretweetstatus'
    )
    comment = models.TextField(blank=True, null=True)
    moderator = models.ForeignKey(
        'moderation.SocialUser',
        verbose_name='Moderator',
        on_delete=models.PROTECT,
        related_name='donotretweetstatus_moderations',
    )
    community = models.ForeignKey(
        'community.Community',
        on_delete=models.PROTECT
    )
    active = models.BooleanField(
        default=True,
        help_text="Is this do not retweet status record active?",
    )

    def __str__(self):
        return "{} {} {}".format(self.status, self.moderator, self.community)

    class Meta:
        verbose_name_plural = "DoNotRetweetStatus"
        constraints = [
            models.UniqueConstraint(
                fields=['id', 'identity'],
                name='versions_id_identity'
            ),
            models.UniqueConstraint(
                fields=['status', 'community'],
                condition=Q(version_end_date__isnull=True),
                name='current_status_community'
            ),
        ] 