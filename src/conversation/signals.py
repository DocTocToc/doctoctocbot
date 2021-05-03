import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Tweetdj
from moderation.models import addsocialuser
from .tasks import handle_normalize
from moderation.models import SocialUser, SocialMedia
from conversation.utils import retweeted_by, quoted_by

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Tweetdj)
def normalize(sender, instance, created, **kwargs):
    if created:
        handle_normalize.apply_async(args=(instance.statusid,), ignore_result=True)
        
@receiver(post_save, sender=Tweetdj)
def socialuser(sender, instance, created, **kwargs):
    if created and not instance.socialuser and instance.json:
        addsocialuser(instance)
        
@receiver(post_save, sender=Tweetdj)
def retweeted_by_receiver(sender, instance, created, **kwargs):
    if created:
        if instance.retweetedstatus:
            retweeted_by(
                rt_statusid = instance.json["retweeted_status"]["id"],
                rt_userid = instance.json["retweeted_status"]["user"]["id"],
                by_socialuserid = instance.socialuser.id
            )
        elif instance.quotedstatus:
            quoted_by(
                quoted_statusid = instance.json["quoted_status"]["id"],
                quoted_userid = instance.json["quoted_status"]["user"]["id"],
                by_socialuserid = instance.socialuser.id
            )