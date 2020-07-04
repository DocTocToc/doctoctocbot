import logging
import datetime
import pytz
from dateutil.relativedelta import relativedelta
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
            # If a version of an object (current or not) was created or deleted
            # for this uid less than one hour ago, do not create a new request
            # queue.
            # This gives enough time for accept / decline tasks to be completed
            queues = Queue.objects.filter(
                uid=uid,
                community=community,
            )
            latest_end: Queue = queues.latest('version_end_date')
            latest_start: Queue = queues.latest('version_start_date')
            latest = get_latest(
                latest_start.version_start_date,
                latest_end.version_end_date
            )
            if latest:
                backoff: int = community.request_queue_backoff * 60 # second
                delta = datetime.datetime.now(pytz.utc) - latest
                delta_seconds = delta.total_seconds()
                logger.debug(f"{delta_seconds=}")
                if delta_seconds < backoff:
                    continue

            accept_pending_q_exists = Queue.objects.current.filter(
                uid=uid,
                community=community,
                state__in=[Queue.ACCEPT, Queue.PENDING],
            ).exists()

            if accept_pending_q_exists:
                continue

            decline_q = Queue.objects.filter(
                uid=uid,
                community=community,
                state=Queue.DECLINE
            )
            # if a request was declined in the past, check its creation
            # datetime
            if decline_q:
                latest = (
                    decline_q.latest('version_end_date') or
                    decline_q.latest('version_start_date')
                )
                logger.debug(f"{latest=}")
                latest_dt = latest.version_start_date
                backoff_hours = community.follow_request_backoff # hours
                backoff_seconds = backoff_hours * 60 * 60
                delta = datetime.datetime.now(pytz.utc) - latest_dt
                delta_seconds = delta.total_seconds()
                logger.debug(f"{delta_seconds=}")

                if delta_seconds < backoff_seconds:
                    continue

            """
            cancel_q_exists = Queue.objects.current.filter(
                uid=uid,
                community=community,
                state=Queue.CANCEL,
            ).exists()
            if cancel_q_exists:
                continue
            """
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
    
def get_latest(latest_start, latest_end):
    if not latest_start and not latest_end:
        return
    if not latest_start and latest_end:
        return latest_end
    if not latest_end and latest_start:
        return latest_start
    if latest_end > latest_start:
        return latest_end
    else:
        return latest_start
    