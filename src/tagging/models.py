from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 
from django.db.utils import DatabaseError

from versions.models import Versionable
from versions.fields import VersionedForeignKey

from community.models import get_default_community
from moderation.models import get_default_socialmedia

from taggit.managers import TaggableManager
from conversation.models import GenericBigIntTaggedItem
from django.contrib.postgres.fields import ArrayField


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
    try:
        return Category.objects.count()
    except DatabaseError:
        return 0
      
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


class TagKeyword(models.Model):
    tag = TaggableManager(through=GenericBigIntTaggedItem)
    keyword = ArrayField(
        models.CharField(
            max_length=255,
            blank=True
        )
    )
    community = models.ManyToManyField(
        "community.Community",
        blank=True    
    )

    def __str__(self):
        tags = []
        for tag in self.tag.all():
            tags.append(str(tag))
        return ', '.join(tags)