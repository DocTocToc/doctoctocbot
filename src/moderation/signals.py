import logging
import random

from django.db.utils import DatabaseError
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from moderation.thumbnail import generate_thumbnail

from dm.api import senddm
from moderation.models import (
    Queue,
    Moderation,
    SocialUser,
    UserCategoryRelationship,
    Category,
    Moderator
)

from .moderate import quickreply
from .tasks import handle_create_update_profile
from .tasks import handle_sendmoderationdm

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Queue)
def create_moderation(sender, instance, created, **kwargs):
    if created:
        logger.debug(f"inside create_moderation {sender}, {instance}, {created}")
        logger.debug(f"inside create_moderation if created {sender}, {instance}, {created}")
        moderatorid_int_lst = []
        if settings.MODERATION["moderator"]:
            #moderatorid_int_lst.extend(SocialUser.objects.moderators())
            moderatorid_int_lst.extend(SocialUser.objects.active_moderators())
        elif settings.MODERATION["dev"]:
            logger.debug(f"SocialUser.objects.devs(): {SocialUser.objects.devs()}")
            moderatorid_int_lst.extend(SocialUser.objects.devs())
        else:
            return
        logger.debug(f"moderatorid_int_lst: {moderatorid_int_lst}")
        if not moderatorid_int_lst:
            moderatorid_int_lst.extend(SocialUser.objects.devs())
        if not moderatorid_int_lst:
            return
        chosenmoderatorid_int = random.choice(moderatorid_int_lst)
        logger.debug(f"chosenmoderatorid_int: {chosenmoderatorid_int}")
        moderator_mi = SocialUser.objects.get(user_id = chosenmoderatorid_int)
        Moderation.objects.create(moderator = moderator_mi, queue = instance)
        
@receiver(post_save, sender=Queue)
def createprofile_queue(sender, instance, created, **kwargs):
    if created:
        logger.debug(f"instance {instance}")
        logger.debug(f"instance.status_id {instance.user_id}")
        handle_create_update_profile.apply_async(args=(instance.user_id,))

@receiver(post_save, sender=UserCategoryRelationship)
def log_usercategoryrelationship(sender, instance, created, **kwargs):
    logger.debug(f"ucr saved: sender: {sender}; instance: {instance}; created: {created}")
    logger.debug(f"instance.social_user.user_id: {instance.social_user.user_id}")
    logger.debug(f"instance.moderator.user_id: {instance.moderator.user_id}")
    logger.debug(f"instance.category: {instance.category}")
    
@receiver(post_save, sender=UserCategoryRelationship)
def moderator(sender, instance, created, **kwargs):
    if created:
        try:
            mod_cat = Category.objects.get(name="moderator")
        except Category.DoesNotExist:
            return
        if instance.category == mod_cat:
            with transaction.atomic():
                try:
                    Moderator.objects.create(socialuser=instance.social_user)
                except DatabaseError:
                    return
            generate_thumbnail()

@receiver(post_save, sender=UserCategoryRelationship)
def createprofile_usercategoryrelationship(sender, instance, created, **kwargs):
    logger.debug(f"instance {instance}")
    logger.debug(f"instance.social_user.user_id {instance.social_user.user_id}")
    handle_create_update_profile.apply_async(args=(instance.social_user.user_id,))
    
@receiver(post_save, sender=Moderation)
def createupdatemoderatorprofile(sender, instance, created, **kwargs):
    if created:
        if not hasattr(instance.moderator, 'profile'):
            logger.debug(f"instance.moderator.user_id: {instance.moderator.user_id}")
            handle_create_update_profile.apply_async(args=(instance.moderator.user_id,))

@receiver(post_save, sender=Moderation)   
def sendmoderationdm(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(
            lambda: handle_sendmoderationdm.apply_async(
                args=(instance.id,),
                countdown=60.0
            )
        )