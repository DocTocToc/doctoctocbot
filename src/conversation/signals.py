import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Tweetdj
from moderation.models import addsocialuser
from .tasks import handle_normalize
from moderation.models import SocialUser, SocialMedia

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Tweetdj)
def normalize(sender, instance, created, **kwargs):
    if created:
        handle_normalize.apply_async(args=(instance.statusid,))
        
@receiver(post_save, sender=Tweetdj)
def socialuser(sender, instance, created, **kwargs):
    if created:
        addsocialuser(instance)