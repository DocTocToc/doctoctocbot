from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
import random

from bot.conf.cfg import getConfig
from dm.api import senddm
from moderation.models import Queue, Moderation, SocialUser

from .moderate import quickreply
from .tasks import handle_create_update_profile
from .tasks import handle_sendmoderationdm


logger = logging.getLogger(__name__)

@receiver(post_save, sender=Queue)
def create_moderation(sender, instance, created, **kwargs):
    logger.debug(f"inside create_moderation {sender}, {instance}, {created}")
    if created:
        logger.debug(f"inside create_moderation if created {sender}, {instance}, {created}")
        moderatorid_int_lst = []
        if getConfig()["moderation"]["moderator"]:
            moderatorid_int_lst.extend(SocialUser.objects.moderators())
        elif getConfig()["moderation"]["dev"]:
            logger.debug(f"SocialUser.objects.devs(): {SocialUser.objects.devs()}")
            moderatorid_int_lst.extend(SocialUser.objects.devs())
        else:
            return
        logger.debug(f"moderatorid_int_lst: {moderatorid_int_lst}")
        chosenmoderatorid_int = random.choice(moderatorid_int_lst)
        logger.debug(f"chosenmoderatorid_int: {chosenmoderatorid_int}")
        moderator_mi = SocialUser.objects.get(user_id = chosenmoderatorid_int)
        Moderation.objects.create(moderator = moderator_mi, queue = instance)
        
@receiver(post_save, sender=Queue)
def createprofile(sender, instance, created, **kwargs):
    logger.debug(f"instance {instance}")
    logger.debug(f"instance.status_id {instance.user_id}")
    handle_create_update_profile.apply_async(args=(instance.user_id,))
    
@receiver(post_save, sender=Moderation)
def createupdatemoderatorprofile(sender, instance, created, **kwargs):
    if not hasattr(instance.moderator, 'profile'):
        logger.debug(f"instance.moderator.user_id: {instance.moderator.user_id}")
        handle_create_update_profile.apply_async(args=(instance.moderator.user_id,))

@receiver(post_save, sender=Moderation)   
def sendmoderationdm(sender, instance, created, **kwargs):
    #transaction.on_commit(lambda: handle_sendmoderationdm(kwargs['instance'].id))
    transaction.on_commit(lambda: handle_sendmoderationdm.apply_async(args=(instance.id,)))