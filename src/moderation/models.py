from django.db import models, connection
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from versions.models import Versionable
from versions.fields import VersionedForeignKey
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe
from os.path import stat
from sys import getprofile

class AuthorizedManager(models.Manager):
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

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    label_en = models.CharField(max_length=255, unique=True)
    label_fr = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name
    
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
    socialuser = models.OneToOneField(SocialUser, on_delete=models.CASCADE)
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
            url = static("twitter_unknown_images/egg24x24.png")
        
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
            url = static("twitter_unknown_images/egg24x24.png")
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
            url = static("twitter_unknown_images/egg24x24.png")
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