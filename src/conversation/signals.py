import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Tweetdj
from moderation.models import addsocialuser

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Tweetdj)
def socialuser(sender, instance, created, **kwargs):
    if created and not instance.socialuser and instance.json:
        addsocialuser(instance)