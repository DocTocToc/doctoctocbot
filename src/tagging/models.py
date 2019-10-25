from django.db import models

from versions.models import Versionable
from versions.fields import VersionedForeignKey

from community.models import get_default_community
from moderation.models import get_default_socialmedia


class Queue(Versionable):
    uid = models.BigIntegerField()
    socialmedia = models.ForeignKey(
        'moderation.SocialMedia',
        on_delete=models.CASCADE,
        default=get_default_socialmedia
    )
    community = models.ForeignKey(
        'community.Community',
        on_delete=models.CASCADE,
        default=get_default_community,
        related_name='%(app_label)s_%(class)s'
    )
    
    def __str__(self):
        return (f"{self.uid} {self.community}")
    
    class Meta:
        unique_together: ('uid', 'socialmedia', 'community')


class Process(Versionable):
    queue = VersionedForeignKey(Queue, on_delete=models.CASCADE)
    processor = models.ForeignKey('moderation.SocialUser',
                                  on_delete=models.CASCADE,
                                  related_name='%(app_label)s_%(class)s')
    
    class Meta:
        unique_together: ('queue', 'processor')

      
class Category(models.Model):
    tag = models.CharField(
        max_length=36,
        unique=True,
    )
    description = models.CharField(max_length=72)
    community = models.ForeignKey(
        'community.Community',
        on_delete=models.CASCADE,
        default=get_default_community,
        related_name='%(app_label)s_%(class)s'
    )