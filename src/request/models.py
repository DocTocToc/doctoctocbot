from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 
from django.db.utils import DatabaseError

from versions.models import Versionable
from versions.fields import VersionedForeignKey

from community.models import get_default_community
from moderation.models import get_default_socialmedia


class Queue(Versionable):
    ACCEPT = 'accept'
    DECLINE = 'decline'
    CANCEL = 'cancel'
    PENDING = 'pending'
    REQUEST_STATE_CHOICES = [
        (ACCEPT, 'Accepted'),
        (DECLINE, 'Declined'),
        (CANCEL, 'Canceled'),
        (PENDING, 'Pending'),
    ]
    uid = models.BigIntegerField()
    socialmedia = models.ForeignKey(
        'moderation.SocialMedia',
        on_delete=models.CASCADE,
        default=get_default_socialmedia,
        related_name='%(app_label)s_%(class)s'
    )
    socialuser = models.ForeignKey('moderation.SocialUser',
                                  on_delete=models.CASCADE,
                                  related_name='%(app_label)s_%(class)s')
    community = models.ForeignKey(
        'community.Community',
        on_delete=models.CASCADE,
        default=get_default_community,
        related_name='%(app_label)s_%(class)s'
    )
    state = models.CharField(
        max_length=7,
        choices=REQUEST_STATE_CHOICES,
        default=PENDING,
    )
    
    def __str__(self):
        return (f"{self.uid} {self.community}")
    
    class Meta:
        unique_together: ('identity', 'uid', 'socialmedia', 'community')
        ordering = ['version_start_date']


class RequestDm(models.Model):
    SENT = 'S'
    FAIL = 'F'
    DM_STATE_CHOICES = [
        (SENT, 'sent'),
        (FAIL, 'failed'),
    ]
    queue =  models.OneToOneField(
        "request.Queue",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    state = models.CharField(
        max_length=1,
        choices=DM_STATE_CHOICES,
        null=True,
    )
    dm_id = models.BigIntegerField(
        null=True,
        default=None,
    )
    error_code = models.PositiveIntegerField(
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)


class RequestStatus(models.Model):
    queue =  VersionedForeignKey(
        'request.Queue',
        on_delete=models.PROTECT,
        unique=True
    )
    status = models.OneToOneField(
        'conversation.Tweetdj',
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return (f"{self.queue} {self.status}")


    class Meta:
        verbose_name_plural = "Request statuses"


"""
class Process(Versionable):
    queue = VersionedForeignKey(Queue, on_delete=models.CASCADE)
    processor = models.ForeignKey('moderation.SocialUser',
                                  on_delete=models.CASCADE,
                                  related_name='%(app_label)s_%(class)s')
    
    def __str__(self):
        return (f"queue:{self.queue} processor:{self.processor}")

    class Meta:
        unique_together = ('queue', 'processor')
        verbose_name_plural = "processes"
"""