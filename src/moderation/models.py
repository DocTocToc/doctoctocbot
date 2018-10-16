from django.db import models, connection
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from versions.models import Versionable
import logging

class AuthorizedManager(models.Manager):
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
        return str(self.user_id)

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
    social_user = models.ForeignKey('SocialUser', on_delete=models.CASCADE, related_name="moderations")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name="relationships")
    moderator = models.ForeignKey('SocialUser', on_delete=models.CASCADE, related_name='moderated', null=True)
    datetimestamp =  models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ("social_user", "category")
    
    
class SocialMedia(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)
        
class Profile(Versionable):
    json = JSONField()
    social_user = models.ForeignKey('SocialUser', on_delete=models.CASCADE, related_name='profiles')
    
    def __str__(self):
        return self.annotate(val=KeyTextTransform('name', 'json')).value('val')

class Queue(Versionable):
    user_id = models.BigIntegerField(unique=True)
    status_id = models.BigIntegerField(unique=True)
    moderator = models.ForeignKey('SocialUser', null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return (f"{self.user_id} {self.status_id} {self.moderator}")