import logging
from django.db.utils import DatabaseError
from django.db.models.signals import post_save
from django.dispatch import receiver
from request.models import Queue, RequestDm
from dm.api import senddm
from django.utils.translation import gettext as _
from moderation.models import Category
from moderation.models import Queue as ModerationQueue
from moderation.twitter.user import TwitterUser
from community.helpers import activate_language
from request.twitter_request import message_requestor
from request.tasks import (
    handle_accept_follower_twitter,
    handle_decline_follower_twitter,
)
from request.utils import request_dm

logger = logging.getLogger(__name__) 

@receiver(post_save, sender=Queue)
def dm_admin(sender, instance, created, **kwargs):
    if (
        created
        and (instance.state == Queue.PENDING)
        and (instance.id == instance.identity)
    ):
        try:
            screen_name = instance.socialuser.screen_name_tag()
        except:
            screen_name = None
        activate_language(instance.community)
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

@receiver(post_save, sender=Queue)
def message_requestor_slot(sender, instance, created, **kwargs):
    if (
        created
        and (instance.state == Queue.PENDING)
        and (instance.id == instance.identity)
    ):
        message_requestor(instance)

@receiver(post_save, sender=Queue)
def create_moderation_queue(sender, instance, created, **kwargs):
    if (
        created
        and (instance.state == Queue.PENDING)
        and (instance.id == instance.identity)
    ):
        try:
            ModerationQueue.objects.create(
                user_id= instance.uid,
                status_id=None,
                community=instance.community,
                type=ModerationQueue.FOLLOWER,
            )
        except DatabaseError:
            return

@receiver(post_save, sender=Queue)
def follower_protected_requestor(sender, instance, created, **kwargs):
    if (
        created
        and (instance.state == Queue.PENDING)
        and (instance.id == instance.identity)
    ):
        twitter_user = TwitterUser(socialuser=instance.socialuser)
        if twitter_user.is_protected():
            twitter_user.friend(instance.community)

@receiver(post_save, sender=Queue)
def accept_decline_autotweet(sender, instance, created, **kwargs):
    is_twitter = instance.socialmedia.name == 'twitter'
    current_version = Queue.objects.current_version(instance)
    if (
        instance.state == Queue.ACCEPT
        and is_twitter
        and current_version
    ):
        return
        """
        handle_accept_follower_twitter.apply_async(
            args=[instance.uid, instance.community.id]
        )
        """
    elif (
        instance.state == Queue.DECLINE
        and is_twitter
        and current_version
    ):
        return
        """
        handle_decline_follower_twitter.apply_async(
            args=[instance.uid, instance.community.id]
        )
        """

@receiver(post_save, sender=Queue)
def request_dm(sender, instance, created, **kwargs):
    if (
        instance.community.twitter_request_dm
        and created
        and (instance.state == Queue.PENDING)
        and (instance.id == instance.identity)
    ):
        has_requestdm = False
        try:
            has_requestdm = (instance.requestdm is not None)
        except RequestDm.DoesNotExist:
            pass
        if not has_requestdm:
            request_dm(instance)