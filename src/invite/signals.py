import logging
logger = logging.getLogger(__name__)

from django.dispatch import receiver
from django.db.utils import DatabaseError
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from invite.models import CategoryInvitation
from invitations.signals import invite_accepted
from moderation.models import (
    SocialUser,
    Category,
    UserCategoryRelationship,
    SocialMedia,
)

User = get_user_model()

@receiver(invite_accepted)
def set_session(sender, **kwargs):
    logger.debug("invite_accepted signal caught!")

@receiver(post_save, sender=User)
def set_category(sender, instance, created, **kwargs):
    if created:
        # This social media
        try:
            social_media = SocialMedia.objects.get(
                name=settings.THIS_SOCIAL_MEDIA
            )
            logger.debug(social_media)
        except SocialMedia.DoesNotExist:
            return
        # Retrieve category and inviter (moderator)
        email: str = instance.email
        logger.debug(email)
        try:
            category_invitation = CategoryInvitation.objects.get(
                email=email,
                accepted=True
            )
            logger.debug(category_invitation)
        except CategoryInvitation.DoesNotExist:
            return
        try:
            category: Category = category_invitation.category
            logger.debug(category)
        except AttributeError:
            return
    
        inviter: User = category_invitation.inviter
        if not inviter:
            logger.error(f"No inviter set for {category_invitation}")
            return
        moderator: SocialUser = inviter.socialuser 
        
        # Create SocialUser
        try:
            social_user = SocialUser.objects.create(
                user_id = instance.id,
                social_media = social_media
            )
            logger.debug(social_user)
        except DatabaseError as e:
            logger.debug(e)
            return
        # Link Django user and SocialUser
        instance.socialuser = social_user
        instance.save()
        # Create UserCategoryRelationship
        try:
            ucr = UserCategoryRelationship.objects.create(
                social_user = social_user,
                category = category,
                moderator = moderator,
            )
            logger.info(
                f"UserCategoryRelationship {ucr} "
                f"created for Django user {instance}"
            )
        except DatabaseError:
            return