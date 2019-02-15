from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Tweetdj
from .tasks import handle_normalize


@receiver(post_save, sender=Tweetdj)
def normalize(sender, instance, created, **kwargs):
    handle_normalize.apply_async(args=(instance.statusid,))