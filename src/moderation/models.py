import logging
from os.path import stat
from sys import getprofile

from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models, connection
from django.contrib.postgres.fields import ArrayField
from django.utils.safestring import mark_safe
from django.conf import settings

from versions.fields import VersionedForeignKey
from versions.models import Versionable


class AuthorizedManager(models.Manager):
    def category_users(self, category):
        """
        Return list of users bigint user_id from a category.
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


    def authorized_users(self):
        """
        Return list of authorized users bigint user_id.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id
                FROM moderation_socialuser
                WHERE id IN
                (
                SELECT social_user_id FROM moderation_usercategoryrelationship WHERE category_id IN
                (SELECT id FROM moderation_category WHERE name = 'physician' OR name = 'midwife')
                );""")
            result = cursor.fetchall()
            logging.debug(result)
        return [row[0] for row in result]

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
            logging.debug(result)
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
            logging.debug(result)
        return [row[0] for row in result]


    def all_users(self):
        """
        Return list of all known users bigint user_id.
        """
        with connection.cursor() as cursor:
            cursor.execute("""SELECT user_id FROM moderation_socialuser;""")
            result = cursor.fetchall()
            logging.debug(result)
        return [row[0] for row in result]

class SocialUser(models.Model):
    user_id = models.BigIntegerField(unique=True)
    social_media = models.ForeignKey('SocialMedia', related_name='users', on_delete=models.CASCADE)
    category = models.ManyToManyField('Category',
                                      through='UserCategoryRelationship',
                                      through_fields=('social_user', 'category'))
    objects = AuthorizedManager()
    
    def __str__(self):
        return str("%i %s " % (self.user_id, self.social_media))

    def normal_image_tag(self):
        return mark_safe('<img src="%s"/>' % (self.profile.normalavatar.url))
    
    normal_image_tag.short_description = 'Image'
    
    def mini_image_tag(self):
        return mark_safe('<img src="%s"/>' % (self.profile.miniavatar.url))
    
    mini_image_tag.short_description = 'Image'   

    def screen_name_tag(self):
        screen_name = self.profile.json.get("screen_name", None)
        return screen_name
    
    screen_name_tag.short_description = 'Screen name'
    
    def name_tag(self):
        name = self.profile.json.get("name", None)
        return name
    
    name_tag.short_description = 'Name'

            

    class Meta:
        ordering = ('user_id',)


class AuthorizedCategoryManager(models.Manager):
    def get_queryset(self):
        name_lst = settings.MODERATION_AUTHORIZED_CATEGORIES
        return super().get_queryset().filter(name__in=name_lst)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    quickreply = models.BooleanField(default=False,
                                         help_text="Include in DM quickreply?")
    socialgraph = models.BooleanField(default=False,
                                         help_text="Include in moderation social graph?")    
    color = models.CharField(max_length=20, unique=True, null=True, blank=True)

    objects = models.Manager()
    authorized = AuthorizedCategoryManager()
    
    def __str__(self):
        return self.name
    
    def clean(self):
        if (self.quickreply and
                Category.objects.filter(quickreply=True).count() > 20):
            raise ValidationError(_('Maximum number of category instances '
                                    ' that can be included in a quickreply is 20.'))
    
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "categories"

    

class UserCategoryRelationship(models.Model):
    social_user = models.ForeignKey('SocialUser', on_delete=models.CASCADE, related_name="categoryrelationships")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="relationships")
    moderator = models.ForeignKey('SocialUser', on_delete=models.CASCADE, related_name='moderated', null=True)
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)

    
    class Meta:
        unique_together = ("social_user", "category")
    
    
class SocialMedia(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)
        
class Profile(models.Model):
    socialuser = models.OneToOneField(SocialUser, on_delete=models.CASCADE, related_name="profile")
    json = JSONField()
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
    
    mini_image_tag.short_description = 'Image'   

    def screen_name_tag(self):
        if self.json is not None:
            screen_name = self.json.get("screen_name", None)
            return screen_name
        else:
            return None
    
    screen_name_tag.short_description = 'Screen name'
    
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
            pass
        description = (
            f'pk: {self.id}'
            f'Profile id: {str(self.json.get("id", None))} '
            f'name: {str(self.json.get("name", None))} '
            f'status: {text}'
        )
        return description

class Queue(Versionable):
    user_id = models.BigIntegerField()
    status_id = models.BigIntegerField()
    
    def __str__(self):
        return (f"{self.user_id} {self.status_id}")
    
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
        from django.contrib.staticfiles.templatetags.staticfiles import static
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
        from conversation.models import Tweetdj
        return Tweetdj.getstatustext(self.status_id)[:140]

    status_tag.short_description = 'Status'      

    
     
    
class Moderation(Versionable):
    moderator = models.ForeignKey(SocialUser,
                                  on_delete=models.CASCADE,
                                  related_name='moderations')
    queue = VersionedForeignKey(Queue, on_delete=models.CASCADE)
    
    def __str__(self):
        try:
            return f'{self.moderator.profile.json["screen_name"]} {self.version_birth_date}'
        except ObjectDoesNotExist:
            return f'{self.moderator.user_id} {self.version_birth_date}'
        
    def status_tag(self):
        status_id = self.queue.status_id
        from conversation.models import Tweetdj
        return Tweetdj.getstatustext(status_id)[:140]
    
    status_tag.short_description = 'Status'      

    def getprofile(self):
        try:
            p = self.moderator.profile
        except Profile.DoesNotExist:
            p = None
        return p

    def moderator_mini_image_tag(self):
        from django.contrib.staticfiles.templatetags.staticfiles import static
        p = getattr(self.moderator, 'profile', None)
        logging.debug(f"profile: {p}")
        if p is not None:
            url = p.miniavatar.url
        else:
            url = static("moderation/twitter_unknown_images/egg24x24.png")
        return mark_safe('<img src="%s"/>' % url)
    
    moderator_mini_image_tag.short_description = 'Moderator image'

    def moderated_mini_image_tag(self):
        from django.contrib.staticfiles.templatetags.staticfiles import static
        userid = self.queue.user_id
        su = SocialUser.objects.get(user_id=userid)
        p = getattr(su, 'profile', None)
        logging.debug(f"profile: {p}")
        if p is not None:
            url = p.miniavatar.url
        else:
            url = static("moderation/twitter_unknown_images/egg24x24.png")
        return mark_safe('<img src="%s"/>' % url)
    
    moderated_mini_image_tag.short_description = 'Moderated image'
    
    def moderator_screen_name_tag(self):
        p = self.moderator.profile
        logging.debug(f"profile: {p}")
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
        logging.debug(f"profile: {p}")
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
    json = JSONField(blank=True, null=True)
    
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
    followers = ArrayField(
        models.BigIntegerField()
        )
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        screen_name = None
        if hasattr(self.user, "profile"):
            screen_name = self.user.profile.json.get("screen_name", None)
        
        name = screen_name or str(self.user.user_id)
        return "followers of %s " % name