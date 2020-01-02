import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from request.models import Queue
from dm.api import senddm
from django.utils.translation import gettext as _
from moderation.models import Category

logger = logging.getLogger(__name__) 

@receiver(post_save, sender=Queue)
def dm_admin(sender, instance, created, **kwargs):
    if created:
        try:
            screen_name = instance.socialuser.profile.screen_name_tag()
        except:
            screen_name = None
        community_name = instance.community.name
        if screen_name:
            text = _("Please handle @{screen_name} follow request for {community_name} community.").format(
                screen_name=screen_name,
                community_name=community_name
            )
        else:
            text = _("You have a new follow request.")
        
        try:
            dev_cat = Category.objects.get(name='dev')
            logger.debug(dev_cat)
        except Category.DoesNotExist:
            return
        try:
            screen_name = instance.community.account.username
        except:
            return
        for dev in dev_cat.socialuser_set.all(): 
            dm = senddm(
                text=text,
                user_id=dev.user_id,
                screen_name=screen_name
            )
            logger.debug(dm)
        
        