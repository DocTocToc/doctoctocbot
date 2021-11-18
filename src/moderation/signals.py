import logging
from django.db.utils import DatabaseError
from django.db import transaction, IntegrityError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from moderation.thumbnail import generate_thumbnail
from moderation.moderate import create_initial_moderation
from community.helpers import get_community_bot_screen_name
from django.db.models import Q

from moderation.models import (
    Queue,
    Moderation,
    SocialUser,
    UserCategoryRelationship,
    Category,
    Moderator,
    Human,
    get_default_socialmedia,
)

from hcp.models import HealthCareProviderTaxonomy, TaxonomyCategory

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Queue)
def create_moderation_receiver(sender, instance, created, **kwargs):
    if created:
        logger.debug(
            f"inside create_moderation_receiver if created:\n"
            f"{sender}, {instance}, {created}"
        )
        create_initial_moderation(instance)

"""
@receiver(post_save, sender=Queue)
def createprofile_queue(sender, instance, created, **kwargs):
    if created:
        logger.debug(f"instance {instance}")
        logger.debug(f"instance.status_id {instance.user_id}")
        try:
            bot_screen_name = instance.community.account.username
        except AttributeError:
            bot_screen_name = None
        handle_create_update_profile.apply_async(
            args=[instance.user_id],
            kwargs={'bot_screen_name': bot_screen_name}
        )
"""

@receiver(post_save, sender=UserCategoryRelationship)
def log_usercategoryrelationship(sender, instance, created, **kwargs):
    if settings.DEBUG:
        logger.debug(f"ucr saved: sender: {sender}; instance: {instance}; created: {created}")
        logger.debug(f"instance.social_user.user_id: {instance.social_user.user_id}")
        if instance.moderator:
            logger.debug(f"instance.moderator.user_id: {instance.moderator.user_id}")
        logger.debug(f"instance.category: {instance.category}")

@receiver([post_save, post_delete], sender=Moderator)
def moderator(sender, instance, **kwargs):
    generate_thumbnail(instance.community)

"""
@receiver(post_save, sender=UserCategoryRelationship)
def createprofile_usercategoryrelationship(sender, instance, created, **kwargs):
    logger.debug(f"instance {instance}")
    logger.debug(f"instance.social_user.user_id {instance.social_user.user_id}")
    bot_screen_name = get_community_bot_screen_name(instance.community)
    handle_create_update_profile.apply_async(
        args=(instance.social_user.user_id,),
        kwargs={'bot_screen_name': bot_screen_name}
    )
"""

"""    
@receiver(post_save, sender=Moderation)
def createupdatemoderatorprofile(sender, instance, created, **kwargs):
    if created:
        if not hasattr(instance.moderator, 'profile'):
            logger.debug(f"instance.moderator.user_id: {instance.moderator.user_id}")
            bot_screen_name = get_community_bot_screen_name(
                instance.queue.community
            )
            handle_create_update_profile.apply_async(
                args=[instance.moderator.user_id],
                kwargs={'bot_screen_name': bot_screen_name}
            )
"""

"""
@receiver(post_save, sender=SocialUser)
def create_update_socialuser_profile(sender, instance, created, **kwargs):
    if created:
        if not hasattr(instance, 'profile'):
            logger.debug(f"instance.user_id: {instance.user_id}")
            handle_create_update_profile.apply_async(args=(instance.user_id,))
"""

@receiver(post_save, sender=SocialUser)
def create_human(sender, instance, created, **kwargs):
    if created:
        try:
            human = Human.objects.get(socialuser=instance)
        except Human.DoesNotExist:
            try:
                human = Human()
                human.save()
                human.socialuser.add(instance)
                human.save()
            except:
                logger.error(
                    f'Database error occured while creating Human object for '
                    f'{instance}.'
                )

"""
@receiver(post_save, sender=Moderation)   
def sendmoderationdm(sender, instance, created, **kwargs):
    if created:
        # Moderation instances are versionable. They get cloned and saved.
        # Make sure this is the first time this versionable entity is saved.
        if not (
            instance.id == instance.identity
            and instance.state == None
        ):
            return
        transaction.on_commit(
            lambda: handle_sendmoderationdm.apply_async(
                args=[],
                kwargs={'mod_instance_id': instance.id},
                countdown=5
                )
            )
"""

@receiver(post_save, sender=UserCategoryRelationship)
def accept_follower(sender, instance, created, **kwargs):
    return
    """
    if created:
        if instance.moderator != instance.social_user:
            handle_accept_follower.apply_async(
                args=[instance.pk],
            )
    """

@receiver(post_save, sender=HealthCareProviderTaxonomy)
def add_category_from_taxonomy(sender, instance, created, **kwargs):
    def get_socialuser_from_human(human: Human):
        return human.socialuser.filter(
            social_media=get_default_socialmedia(),
            active=True
        ).first()

    def add_usercategoryrelationship(hcpt, tc):
        social_user = get_socialuser_from_human(hcpt.healthcareprovider.human)
        moderator = get_socialuser_from_human(hcpt.creator)
        if not social_user or not moderator:
            return
        try:
            with transaction.atomic():
                ucr = UserCategoryRelationship.objects.create(
                    social_user=social_user,
                    moderator=moderator,
                    category=tc.category,
                    community=tc.community,
                )
        except IntegrityError as e:
            logger.error(e)

    taxonomy = instance.taxonomy
    qs = TaxonomyCategory.objects.filter(
        Q(code=taxonomy.code) | \
        Q(grouping=taxonomy.grouping) | \
        Q(classification=taxonomy.classification) | \
        Q(specialization=taxonomy.specialization)
    )
    for tc in qs:
        add_usercategoryrelationship(instance, tc)