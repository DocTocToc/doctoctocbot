import logging
from celery import shared_task
from community.models import Community
from request.twitter_request import get_incoming_friendship
from request.models import Queue
from moderation.models import addsocialuser_from_userid, SocialMedia
from moderation.tasks import handle_create_update_profile
from django.db.utils import DatabaseError
from moderation.profile import create_update_profile_twitter
from autotweet.accept import accept_follower, decline_follower
from moderation.social import update_social_ids

logger = logging.getLogger(__name__)

@shared_task
def handle_incoming_friendship():
    for community in Community.objects.all():
        try:
            bot_screen_name = community.account.username
        except:
            continue
        ifs = get_incoming_friendship(community)
        if not ifs:
            continue
        for uid in ifs:
            accept_pending_q_exists = Queue.objects.current.filter(
                uid=uid,
                community=community,
                state__in=[Queue.ACCEPT, Queue.PENDING],
            ).exists()
            if accept_pending_q_exists:
                continue

            decline_q_exists = Queue.objects.current.filter(
                uid=uid,
                community=community,
                state=Queue.DECLINE
            ).exists()
            if decline_q_exists:
                continue
            
            cancel_q_exists = Queue.objects.current.filter(
                uid=uid,
                community=community,
                state=Queue.CANCEL,
            ).exists()
            if cancel_q_exists:
                continue

            try:
                socialmedia = SocialMedia.objects.get(name='twitter')
            except SocialMedia.DoesNotExist:
                return
            socialuser = addsocialuser_from_userid(uid)
            if not socialuser:
                return
            try:
                create_update_profile_twitter(
                    socialuser,
                    bot_screen_name=bot_screen_name
                )
            except:
                continue
            try:
                Queue.objects.create(
                    uid=uid,
                    socialmedia=socialmedia,
                    socialuser=socialuser,
                    community=community,
                    state=Queue.PENDING
                )
            except DatabaseError:
                continue

@shared_task
def handle_accept_follower_twitter(userid: int, community__id: int):
    try:
        community = Community.objects.get(id=community__id)
    except Community.DoesNotExist:
        return
    try:
        username = community.account.username
    except AttributeError as e:
        logger.error(f"Could not get username from community's account: {e}")
        return
    if userid in update_social_ids(
        user=userid,
        cached=False,
        bot_screen_name=username,
        relationship="followers"
    ):
        return
    accept_follower(
        userid,
        username,
    )

@shared_task
def handle_decline_follower_twitter(userid: int, community__id: int):
    try:
        community = Community.objects.get(id=community__id)
    except Community.DoesNotExist as e:
        logger.error(f"Community does not exist: {e}")
        return
    try:
        username = community.account.username
    except AttributeError as e:
        logger.error(f"Could not get username from community's account: {e}")
        return
    decline_follower(
        userid,
        username,
    )