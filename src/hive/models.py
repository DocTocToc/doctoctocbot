from django.db import models
from datetime import timedelta
from constance import config
from django.utils.dateparse import parse_duration
from django.core.validators import MinValueValidator

def retweet_count_min_value():
    return config.hive__models__tweetsubscription__retweet_count_min_value

def default_age():
    duration = config.hive__models__tweetsubscription__age
    return parse_duration(duration)


class TweetSubscription(models.Model):
    socialuser = models.ForeignKey(
        'moderation.SocialUser',
        on_delete=models.CASCADE,
        related_name="tweetsubscription",
    )
    language = models.ManyToManyField(
        'conversation.TwitterLanguageIdentifier',
        blank=True,
    )
    quote_count = models.PositiveIntegerField(
        null=True,
        blank=True, 
    )
    retweet_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(retweet_count_min_value)]
    )
    broadcast_count = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    category = models.ManyToManyField(
        'moderation.Category',
        blank=True,
    )
    service = models.ManyToManyField(
        'hive.NotificationService',
        blank=True,
    )
    age = models.DurationField(
        default=default_age    
    )
    active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return '%s %s' % (self.socialuser, self.active)


class NotificationService(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True
    )
    label = models.CharField(
        max_length=255,
    )
    description = models.TextField(
        blank=True,
    )    

    def __str__(self):
        return '%s' % (self.name)


class NotificationLog(models.Model):
    statusid = models.BigIntegerField()
    tweetsubscription = models.ForeignKey(
        'hive.TweetSubscription',
        on_delete=models.PROTECT,
        related_name="log",
    )
    socialuser = models.ForeignKey(
        'moderation.SocialUser',
        on_delete=models.PROTECT,
        related_name="notificationlog",
    )
    service = models.ForeignKey(
        'hive.NotificationService',
        on_delete=models.CASCADE,
        related_name="notificationlog",
    )
    success = models.BooleanField(
        null=True,
        blank=True,
    )
    success_log = models.JSONField(
        null = True    
    )
    error_log = models.JSONField(
        null = True    
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True
    )
    
    def __str__(self):
        return '%s %s %s %s %s' % (
            self.statusid,
            self.tweetsubscription,
            self.service,
            self.success,
            self.created,
        )