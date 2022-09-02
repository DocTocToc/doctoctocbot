import logging
from django.db.utils import DatabaseError
from django.db.models.signals import post_save
from django.dispatch import receiver
from request.models import Queue as RequestQueue, RequestDm
from dm.api import senddm
from django.utils.translation import gettext as _
from moderation.models import Category
from moderation.models import Queue as ModerationQueue
from moderation.twitter.user import TwitterUser
from community.helpers import activate_language
from request.tasks import (
    handle_accept_follower_twitter,
    handle_decline_follower_twitter,
)
from request.utils import request_dm
from moderation.moderate import create_initial_moderation
from moderation.filter import QueueFilter

logger = logging.getLogger(__name__) 

@receiver(post_save, sender=RequestQueue)
def dm_admin(sender, instance, created, **kwargs):
    if (
        created
        and (instance.state == RequestQueue.PENDING)
        and (instance.id == instance.identity)
        and instance.version_end_date is None
    ):
        try:
            screen_name = instance.socialuser.screen_name_tag()
        except:
            screen_name = None
        activate_language(instance.community)
        community_name = instance.community.name
        if screen_name:
            text = _("Please handle {tag} follow request for {community_name} community.").format(
                tag=f'@{screen_name}',
                community_name=community_name
            )
        else:
            if instance.socialmedia.name == "twitter":
                tag = f"https://twitter.com/intent/user?user_id={instance.uid}"
            else:
                tag = instance.uid
            text = _("Please handle {tag} follow request for {community_name} community.").format(
                tag=tag,
                community_name=community_name
            )
        try:
            dev_cat = Category.objects.get(name='dev')
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
                bot_screen_name=screen_name
            )
            logger.debug(dm)

@receiver(post_save, sender=RequestQueue)
def create_moderation_queue(sender, instance, created, **kwargs):
    if (
        created
        and (instance.state == RequestQueue.PENDING)
        and (instance.id == instance.identity)
    ):
        qf = QueueFilter(instance.community, instance.socialuser)
        if qf.start_moderation():
            type = ModerationQueue.FOLLOWER
        else:
            type = ModerationQueue.ONHOLD
        try:
            queue = ModerationQueue.objects.create(
                user_id= instance.uid,
                status_id=None,
                community=instance.community,
                type=type,
            )
        except DatabaseError:
            logger.error(f"Creation of moderation queue for {instance} failed")
            return
        create_initial_moderation(queue)

@receiver(post_save, sender=RequestQueue)
def follower_protected_requestor(sender, instance, created, **kwargs):
    if (
        created
        and (instance.state == RequestQueue.PENDING)
        and (instance.id == instance.identity)
    ):
        twitter_user = TwitterUser(socialuser=instance.socialuser)
        if twitter_user.is_protected():
            twitter_user.friend(instance.community)

@receiver(post_save, sender=RequestQueue)
def accept_decline_autotweet(sender, instance, created, **kwargs):
    is_twitter = instance.socialmedia.name == 'twitter'
    current_version = RequestQueue.objects.current_version(instance)
    if (
        instance.state == RequestQueue.ACCEPT
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
        instance.state == RequestQueue.DECLINE
        and is_twitter
        and current_version
    ):
        logger.debug(f"declining follow request for user id={instance.uid}")
        handle_decline_follower_twitter.apply_async(
            args=[instance.uid, instance.community.id]
        )

@receiver(post_save, sender=RequestQueue)
def request_dm_receiver(sender, instance, created, **kwargs):
    if (
        instance.community.twitter_request_dm
        and created
        and (instance.state == RequestQueue.PENDING)
        and (instance.id == instance.identity)
        and instance.version_end_date is None

    ):
        has_requestdm = False
        try:
            has_requestdm = (instance.requestdm is not None)
        except RequestDm.DoesNotExist:
            pass
        if not has_requestdm:
            request_dm(instance)