from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 

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
        unique_together = ('queue', 'processor')
        verbose_name_plural = "processes"


def max_value():
    return Category.objects.count()
      
class Category(models.Model):
    tag = models.CharField(
        max_length=36,
        unique=True,
    )
    summary = models.CharField(max_length=72)
    description = models.TextField()
    community = models.ForeignKey(
        'community.Community',
        on_delete=models.CASCADE,
        default=get_default_community,
        related_name='%(app_label)s_%(class)s'
    )
    order = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(max_value)
        ],
        blank=True,
        null=True
    )
    hashtag = models.BooleanField(
        default=False,
        null=True
    )
    
    class Meta:
        verbose_name_plural = "categories"
        ordering = ["order", "tag"]

