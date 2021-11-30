import logging
from datetime import date
from os.path import stat
from sys import getprofile
from typing import List
import json
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import connection
from django.db.utils import DatabaseError
from django.contrib.postgres.fields import ArrayField
from django.utils.safestring import mark_safe
from django.conf import settings
from django.templatetags.static import static

from versions.fields import VersionedForeignKey
from versions.models import Versionable
from community.models import Community
from django.contrib.sites.shortcuts import get_current_site
from bot.tweepy_api import get_api
from tweepy.error import TweepError
from conversation.models import Tweetdj
from optin.models import Option

logger = logging.getLogger(__name__)

def get_default_community():
    return None

class AuthorizedManager(models.Manager):
    def get_by_natural_key(self, user_id):
        return self.get(user_id=user_id)

    def category_users(self, category: str):
        """
        Return list of users bigint user_id from a category name
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id
                FROM moderation_socialuser
                WHERE id IN
                (
                SELECT social_user_id FROM moderation_usercategoryrelationship WHERE category_id IN
                (SELECT id FROM moderation_category WHERE name = %s)
                );
                """,
                [category]
            )
            result = cursor.fetchall()
        return [row[0] for row in result]

    def physician_users(self):
        """
        Return list of physician users bigint user_id.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id
                FROM moderation_socialuser
                WHERE id IN
                (
                SELECT social_user_id FROM moderation_usercategoryrelationship WHERE category_id IN
                (SELECT id FROM moderation_category WHERE name = 'physician')
                );""")
            result = cursor.fetchall()
        return [row[0] for row in result]
    
    def moderated_users(self):
        """
        Return list of user ids of users who have a category.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id
                FROM moderation_socialuser
                WHERE id IN
                (
                SELECT social_user_id FROM moderation_usercategoryrelationship
                );""")
            result = cursor.fetchall()
        return [row[0] for row in result]

    def active_moderators(self, community: Community, senior=False):
        mod_qs = Moderator.objects.filter(
            active=True,
            community=community
        )
        if senior:
            mod_qs = mod_qs.filter(senior=True)
        try:
            return SocialUser.objects.filter(
                moderator__in=mod_qs
                ).values_list('user_id', flat=True)
        except:
            return []
            
 
    def moderators(self):
        """
        Return a list of BIGINTs representing moderator user_id.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id
                FROM moderation_socialuser
                WHERE id IN
                (
                SELECT social_user_id FROM moderation_usercategoryrelationship WHERE category_id IN
                (SELECT id FROM moderation_category WHERE name = 'moderator')
                );""")
            result = cursor.fetchall()
            #logging.debug(result)
        return [row[0] for row in result]
    
    def devs(self):
        """
        Return a list of BIGINTs representing devs user_id.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id
                FROM moderation_socialuser
                WHERE id IN
                (
                SELECT social_user_id FROM moderation_usercategoryrelationship WHERE category_id IN
                (SELECT id FROM moderation_category WHERE name = 'dev')
                );""")
            result = cursor.fetchall()
            #logging.debug(result)
        return [row[0] for row in result]


    def all_users(self):
        """
        Return list of all known users bigint user_id.
        """
        with connection.cursor() as cursor:
            cursor.execute("""SELECT user_id FROM moderation_socialuser;""")
            result = cursor.fetchall()
            #logging.debug(result)
        return [row[0] for row in result]


class Human(models.Model):
    socialuser = models.ManyToManyField(
        'SocialUser',
        blank=True,
    )
    djangouser = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
    )
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)

    def __str__(self):
        su = self.socialuser.all().first()
        user = self.djangouser.all().first()
        return f"{self.pk} || {su} || {user}"


class SocialUser(models.Model):
    user_id = models.BigIntegerField(unique=True)
    social_media = models.ForeignKey(
        'SocialMedia',
        related_name='users',
        on_delete=models.CASCADE
    )
    category = models.ManyToManyField(
        'Category',
        through='UserCategoryRelationship',
        through_fields=('social_user', 'category')
    )
    twitter_follow_request = models.ManyToManyField(
        'SocialUser',
        related_name="follow_request_by",
        blank=True,
        help_text='Twitter users with pending follow request for this user'
    )
    twitter_block = models.ManyToManyField(
        'SocialUser',
        related_name="block_by",
        blank=True,
        help_text='Twitter users blocked by this user'
    )
    active = models.BooleanField(
        default=True,
        help_text=(
            "Is this SocialUser active? For Twitter, not active means "
            "deactivated or deleted."
        )
    )
    created =  models.DateTimeField(auto_now_add=True, null=True)
    updated =  models.DateTimeField(auto_now=True, null=True)

    objects = AuthorizedManager()

    def __str__(self):
        try:
            return f'{self.pk} | {self.screen_name_tag()} | {self.user_id}'
        except Profile.DoesNotExist:
            return str("%i | %i | %s " % (self.pk, self.user_id, self.social_media))

    def normal_image_tag(self):
        return mark_safe('<img src="%s"/>' % (self.profile.normalavatar.url))
    
    normal_image_tag.short_description = 'Image'
    
    def mini_image_tag(self):
        return mark_safe('<img src="%s"/>' % (self.profile.miniavatar.url))
    
    mini_image_tag.short_description = 'Image'

    def screen_name_tag(self):
        try:
            _json = self.profile.json
        except (Profile.DoesNotExist, AttributeError) as e:
            return
        if not _json:
            return
        if isinstance(_json, str):
            logger.debug("_json is string")
            _json = json.loads(_json)
        return _json.get("screen_name", None)
    
    screen_name_tag.short_description = 'Screen name'
    
    def name_tag(self):
        try:
            return self.profile.json.get("name", None)
        except Profile.DoesNotExist:
            return
        except AttributeError:
            return
    
    name_tag.short_description = 'Name'

    def self_moderate(self, category_name: str, community: Community):
        if not category_name or not community:
            return
        try:
            category: Category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            return
        try:
            with transaction.atomic():
                ucr = UserCategoryRelationship.objects.create(
                    social_user = self,
                    category = category,
                    moderator = self,
                    community = community,
                )
                logger.info(f'Created {ucr}')
        except DatabaseError:
            return

    def community(self) -> List:
        community_lst = []
        for category in self.category.all():
            for community in category.member_of.all():
                community_lst.append(community)
        return community_lst

    def twitter_followers_count(self):
        try:
            return len(self.follower_set.latest().id_list)
        except Follower.DoesNotExist as e:
            logger.error(f'{e}')
        except Exception as e:
            logger.error(f'{e}')


    class Meta:
        ordering = ('user_id',)
        get_latest_by = "user_id"


    def natural_key(self):
        return (self.user_id,)


class CategoryBase(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True
    )
    label = models.CharField(
        max_length=36,
        unique=True,
    )
    description = models.CharField(
        max_length=72,
        blank=True,
        null=True
    )


    class Meta:
        abstract = True


class CategoryManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Category(CategoryBase):
    """
    TODO: link to future community fk, make (label, community) unique together
    """
    mesh = models.ForeignKey(
        'mesh.Mesh',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Category as a MeSH heading",
        related_name="category"
    ) 
    field = models.ForeignKey(
        'mesh.Mesh',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Field as a MeSH heading",
        related_name="category_field",
    )
    public = models.BooleanField(
        default=False,
        help_text=(
            "Should this category be public (visible to users) "
            "or private (for internal use)?"
        )
    )
    
    objects = CategoryManager()

    def __str__(self):
        return self.name
    
    def twitter_screen_name(self):
        communities =  self.community.all()
        if not communities:
            return
        return communities[0].account.username
    
    def twitter_id_list(self):
        """ Return list of Twitter user ids for this category
        """
        return list(
            self.relationships.values_list("social_user__user_id", flat=True)
        )


    class Meta:
        ordering = ('name',)
        verbose_name_plural = "categories"


    def natural_key(self):
        return (self.name,)


class CategoryMetadata(CategoryBase):
    """Manage metadata answers for Quick Replies such as "stop", "I don't know"
    """
    dm = models.BooleanField(
        default=False,
        help_text="Add to DM Quick Reply list?"
    )
    self_dm = models.BooleanField(
        default=False,
        help_text="Add to self Moderation DM Quick Reply list?"
    )


    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Category Metadata"
        
    def __str__(self):
        return self.name


class UserCategoryRelationship(models.Model):
    social_user = models.ForeignKey(
        'SocialUser',
        on_delete=models.CASCADE,
        related_name="categoryrelationships"
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name="relationships"
    )
    moderator = models.ForeignKey(
        'SocialUser',
        on_delete=models.CASCADE,
        related_name='moderated',
        null=True,
        blank=True,
    )
    community = models.ForeignKey(
        'community.Community',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.moderator:
            screen_name = self.moderator.screen_name_tag()
        else:
            screen_name = None
        return (f"su:{self.social_user.screen_name_tag()} ,"
                f"cat:{self.category.name} ,"
                f"mod:{screen_name} ,"
                f"com:{self.community}")

    
    class Meta:
        unique_together = ("social_user", "moderator", "category", "community")
        get_latest_by = "created"


def get_sentinel_social_media():
    return SocialMedia.objects.get_or_create(
        name="deleted",
        emoji="␡",
    )[0]

def get_sentinel_social_media_id():
    return get_sentinel_social_media().id


class SocialMedia(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True
    )
    emoji = models.CharField(
        max_length=255,
        unique=True,
        null = True,
        blank = True,
        help_text = "emoji symbolizing a SocialMedia object for admin pages"
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)
        
def get_default_socialmedia():
    try:
        socialmedia = SocialMedia.objects.order_by('id').first()
        if socialmedia:
            return socialmedia.pk
    except SocialMedia.DoesNotExist as e:
        logger.debug("Create at least one SocialMedia object.", e)

     
class Profile(models.Model):
    socialuser = models.OneToOneField(SocialUser, on_delete=models.CASCADE, related_name="profile")
    json = models.JSONField(default=dict)
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)
    normalavatar = models.ImageField(upload_to='twitter/profile/images/normal',
                                     default='twitter/profile/images/normal/default_profile_normal.png')
    biggeravatar = models.ImageField(upload_to='twitter/profile/images/bigger',
                                     default='twitter/profile/images/bigger/default_profile_bigger.png')
    miniavatar = models.ImageField(upload_to='twitter/profile/images/mini',
                                   default='twitter/profile/images/mini/default_profile_mini.png')

    def mini_image_tag(self):
        return mark_safe('<img src="%s"/>' % (self.miniavatar.url))
    
    def get_normalavatar_url(self, obj):
        return obj.normalavatar.url
    
    mini_image_tag.short_description = 'Image'   

    def screen_name_tag(self):
        _json = self.json
        if not _json:
            return None
        if isinstance(_json, str):
            _json = json.loads(_json.replace("\'", "\""))
        return _json.get("screen_name", None)
    
    screen_name_tag.short_description = 'Screen name'
    
    def follower_count(self):
        try:
            return self.json.get("followers_count")
        except AttributeError:
            return

    follower_count.short_description = "Follower count"

    def name_tag(self):
        if self.json is not None:
            name = self.json.get("name", None)
            return name
        else:
            return None
    
    name_tag.short_description = 'Name'

    def __str__(self):
        try:
            text = self.json["status"]["text"][:140]
        except KeyError:
            text = None
        description = (
            f'pk: {self.id}'
            f'Profile id: {str(self.json.get("id", None))} '
            f'name: {str(self.json.get("name", None))} '
            f'status: {text}'
        )
        return description



class Queue(Versionable):
    MODERATOR = 'moderator'
    SENIOR = 'senior'
    DEVELOPER = 'developer'
    FOLLOWER = 'follower'
    SELF = 'self'
    QUEUE_TYPE_CHOICES = [
        (MODERATOR, _('Moderator')),
        (SENIOR, _('Senior')),
        (DEVELOPER, _('Developer')),
        (FOLLOWER, _('Follower')),
        (SELF, _('Self')),
    ]
    user_id = models.BigIntegerField()
    status_id = models.BigIntegerField(
        null=True,
    )
    community = models.ForeignKey(
        'community.Community',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    type = models.CharField(
        max_length=9,
        choices=QUEUE_TYPE_CHOICES,
        default=MODERATOR,
    )
    
    def __str__(self):
        return (f"Queue {self.user_id} {self.status_id} {self.type}")

    class Meta:
        ordering = ['-version_start_date']


    def profile(self):
        try:
            su = SocialUser.objects.get(user_id=self.user_id)
        except SocialUser.DoesNotExist:
            return None
        
        if hasattr(su, 'profile'):
            return su.profile
        else:
            return None
    
    def mini_image_tag(self):
        if self.profile() is not None:
            p = self.profile()
            url = p.miniavatar.url
        else:
            url = static("moderation/twitter_unknown_images/egg24x24.png")
        
        return mark_safe('<img src="%s"/>' % url)
    
    mini_image_tag.short_description = 'Image'
    
    def screen_name_tag(self):
        if self.profile() is not None:
            p = self.profile()
            screen_name = p.json.get("screen_name", None)
            return screen_name
        else:
            return None
    
    screen_name_tag.short_description = 'Screen name'
    
    def name_tag(self):
        if self.profile() is not None:
            p = self.profile()
            
            name = p.json.get("name", None)
            return name
        else:
            return None
    
    name_tag.short_description = 'Name'      
    
    def status_tag(self):
        return Tweetdj.getstatustext(self.status_id)[:140]

    status_tag.short_description = 'Status'      


class Moderation(Versionable):
    moderator = models.ForeignKey(
        SocialUser,
        on_delete=models.CASCADE,
        related_name='moderations'
    )
    queue = VersionedForeignKey(
        Queue,
        on_delete=models.CASCADE
    )
    state = models.ForeignKey(
        CategoryMetadata,
        on_delete=models.CASCADE,
        related_name='moderations',
        null=True,
        blank=True,
    )


    class Meta:
        ordering = ['-version_start_date']

    
    def __str__(self):
        try:
            return f'{self.moderator.profile.json["screen_name"]} {self.version_birth_date}'
        except ObjectDoesNotExist:
            return f'{self.moderator.user_id} {self.version_birth_date}'
        
    def status_tag(self):
        status_id = self.queue.status_id
        return Tweetdj.getstatustext(status_id)[:140]
    
    status_tag.short_description = 'Status'      

    def getprofile(self):
        try:
            p = self.moderator.profile
        except Profile.DoesNotExist:
            p = None
        return p

    def moderator_mini_image_tag(self):
        p = getattr(self.moderator, 'profile', None)
        #logging.debug(f"profile: {p}")
        if p is not None:
            url = p.miniavatar.url
        else:
            url = static("moderation/twitter_unknown_images/egg24x24.png")
        return mark_safe('<img src="%s"/>' % url)
    
    moderator_mini_image_tag.short_description = 'Moderator image'

    def moderated_mini_image_tag(self):
        userid = self.queue.user_id
        su = SocialUser.objects.get(user_id=userid)
        p = getattr(su, 'profile', None)
        #logging.debug(f"profile: {p}")
        if p is not None:
            url = p.miniavatar.url
        else:
            url = static("moderation/twitter_unknown_images/egg24x24.png")
        return mark_safe('<img src="%s"/>' % url)
    
    moderated_mini_image_tag.short_description = 'Moderated image'
    
    def moderator_screen_name_tag(self):
        try:
            p = self.moderator.profile
        except Profile.DoesNotExist as e:
            logger.warn(e)
            return
        #logging.debug(f"profile: {p}")
        if p is not None:
            screen_name = p.json.get("screen_name", None)
            return screen_name
        else:
            return None
    
    moderator_screen_name_tag.short_description = 'Moderator screen name'
        
    def moderated_screen_name_tag(self):
        userid = self.queue.user_id
        su = SocialUser.objects.get(user_id=userid)
        p = getattr(su, 'profile', None)
        #logging.debug(f"profile: {p}")
        if p is not None:
            screen_name = p.json.get("screen_name", None)
            return screen_name
        else:
            return None
    
    moderated_screen_name_tag.short_description = 'Moderated screen name'
    
class TwitterList(models.Model):
    list_id = models.BigIntegerField(unique=True)
    slug = models.CharField(max_length=25, unique=True)
    name = models.CharField(max_length=25, unique=True)
    twitter_description = models.TextField(blank=True, null=True)
    uid = models.CharField(max_length=25, blank=True, null=True)
    label = models.CharField(max_length=50, blank=True, null=True)
    local_description = models.TextField(blank=True, null=True)
    json = models.JSONField(blank=True, null=True)
    community = models.ForeignKey(
        'community.Community',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    
    def __str__(self):
        if self.uid:
            return f'{self.uid}'
        else:
            return f'{self.slug}'
        
class Follower(models.Model):
    user = models.ForeignKey(
        SocialUser,
        on_delete=models.CASCADE
    )
    id_list = ArrayField(
        models.BigIntegerField(),
        null=True,
        blank=True
        )
    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        get_latest_by = 'created'


    def __str__(self):
        screen_name = None
        if hasattr(self.user, "profile"):
            screen_name = self.user.profile.json.get("screen_name", None)
        
        name = screen_name or str(self.user.user_id)
        return "followers of %s " % name


class Friend(models.Model):
    user = models.ForeignKey(
        SocialUser,
        on_delete=models.CASCADE
    )
    id_list = ArrayField(
        models.BigIntegerField(),
        null=True,
        blank=True
        )
    created = models.DateTimeField(auto_now_add=True)


    class Meta:
        get_latest_by = 'created'


    def __str__(self):
        screen_name = None
        if hasattr(self.user, "profile"):
            screen_name = self.user.profile.json.get("screen_name", None)
        
        name = screen_name or str(self.user.user_id)
        return "friends of %s " % name


class Moderator(models.Model):
    socialuser = models.ForeignKey(
        'moderation.SocialUser',
        on_delete=models.CASCADE,
        related_name='moderator',
    )
    active = models.BooleanField(
        default=False,
        help_text="Is this moderator active?"
    )
    public = models.BooleanField(
        default=True,
        help_text="Does this moderator want to appear on the public list?"
    )
    community = models.ForeignKey(
        'community.Community',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    senior = models.BooleanField(
        default=False,
        help_text="Is this moderator a seasoned moderator?",
    )
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated =  models.DateTimeField(auto_now=True, null=True)

    class Meta:
        unique_together = ['socialuser', 'community']


    def __str__(self):
        try:
            return self.socialuser.profile.json["screen_name"]
        except Profile.DoesNotExist as e:
            logger.warn(e)
            return str("%i %s " % (self.socialuser.user_id, self.socialuser.social_media))
    
    @staticmethod
    def has_read_permission(self):
        return True

    def has_write_permission(self):
        return False
    
    def has_update_permission(self):
        return True
    
    def has_object_read_permission(self, request):
        logger.debug(f"request.user.socialuser: {request.user.socialuser}")
        logger.debug(f"self.socialuser: {self.socialuser}")
        try:
            return (
                request.user.socialuser == self.socialuser and
                self.community == get_current_site(request).community
            )
        except:
            return False

    def has_object_write_permission(self, request):
        return False

    def has_object_update_permission(self, request):
        logger.debug("(request.user.socialuser == self.socialuser) = %s" % (request.user.socialuser == self.socialuser))
        try:
            return (
                request.user.socialuser == self.socialuser and
                self.community == get_current_site(request).community
            )
        except:
            return False

class Image(models.Model):
    name = models.CharField(max_length=255, unique=True)
    img = models.ImageField(null=True,
                          blank=True,
                          upload_to='moderation/')
    def __str__(self):
        return self.name

class DoNotRetweet(models.Model):
    socialuser = models.ForeignKey(
        SocialUser,
        verbose_name='socialuser',
        on_delete=models.CASCADE,
        related_name='donotretweet'
    )
    current = models.BooleanField(
        default=True,
        help_text="Is this row current?"
    )
    start = models.DateField(default=date.today)
    stop = models.DateField(default=date.today)
    comment = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)   
    WARN = 'W'
    MODERATE = 'M'
    BAN = 'B'
    DNR_CHOICES = [
        (WARN, _('Warn')),
        (MODERATE, _('Moderate')),
        (BAN, _('Ban')),
    ]
    action = models.CharField(
        max_length=1,
        choices=DNR_CHOICES,
        default=WARN,
    )
    moderator = models.ForeignKey(
        SocialUser,
        verbose_name='Moderator',
        on_delete=models.CASCADE,
        related_name='donotretweet_moderations',
        null=True,
        blank=True,
    )


    def __str__(self):
        return "{} {}".format(self.socialuser, self.current)


class ModerationOptIn(models.Model):
    """Algorithm followed to create or update moderation related OptIns
    """
    type = models.CharField(
        max_length=9,
        choices=Queue.QUEUE_TYPE_CHOICES
    ) 
    option = models.ForeignKey(
        Option,
        verbose_name='OptIn option',
        on_delete=models.PROTECT,
    )
    authorize = models.BooleanField(
        default=None
    )

    def __str__(self):
        return "{} {} {}".format(self.type, self.option, self.authorize)    


def addsocialuser(tweetdj_instance):
    su = addsocialuser_from_userid(tweetdj_instance.userid)
    if not su:
        return
    tweetdj_instance.socialuser=su
    tweetdj_instance.save()

def addsocialuser_from_userid(userid: int):
    try:
        su = SocialUser.objects.get(user_id=userid)
    except SocialUser.DoesNotExist:    
        try:
            sm, _ = SocialMedia.objects.get_or_create(name="twitter")
        except DatabaseError as e:
            logger.error(e)
            return
        try:
            su, _ = SocialUser.objects.get_or_create(
                user_id=userid,
                social_media = sm
            )
        except DatabaseError as e:
            logger.error(e)
            return
    return su


class Prospect(models.Model):
    socialuser = models.ForeignKey(
        'moderation.SocialUser',
        on_delete=models.PROTECT,
    )
    community = models.ForeignKey(
        'community.Community',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    active = models.BooleanField(
        default=True,
        help_text=(
            "Is this Prospect active?"
        )
    )
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} {} {}".format(self.socialuser, self.community, self.active)
    
    class Meta:
        unique_together = ['socialuser', 'community']