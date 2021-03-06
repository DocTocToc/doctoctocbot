import logging
from datetime import datetime
import pytz
from typing import Optional
from dateutil.relativedelta import relativedelta
from celery import shared_task
from community.models import Community
from request.twitter_request import get_incoming_friendship
from request.models import Queue
from moderation.models import addsocialuser_from_userid, SocialMedia
from django.db.utils import DatabaseError
from moderation.profile import create_update_profile_twitter
from autotweet.accept import accept_follower, decline_follower
from moderation.social import update_social_ids
from request.utils import update_request_queue

logger = logging.getLogger(__name__)

"""Create a queue
"""
def create_queue(community, uid, bot_screen_name):
    try:
        socialmedia = SocialMedia.objects.get(name='twitter')
    except SocialMedia.DoesNotExist:
        return
    socialuser = addsocialuser_from_userid(uid)
    if not socialuser:
        return
    create_update_profile_twitter(
            socialuser,
            bot_screen_name=bot_screen_name,
            cache=False
    )
    try:
        Queue.objects.create(
            uid=uid,
            socialmedia=socialmedia,
            socialuser=socialuser,
            community=community,
            state=Queue.PENDING
        )
    except DatabaseError as e:
        logger.error(f"Database error during Request Queue creation; {e}")

""" Return True if current pending request queue exists
"""
def pending_request_exists(community, uid):
    return Queue.objects.current.filter(
        uid=uid,
        community=community,
        state=Queue.PENDING
    ).exists()

""" Return True if current accepted request queue exists
"""
def accept_request_exists(community, uid):
    return Queue.objects.current.filter(
        uid=uid,
        community=community,
        state=Queue.ACCEPT
    ).exists()

""" Return True if time elapsed since last declined request for this
    community / user pair is less than follow_request_backoff
"""
def decline_backoff(community, uid):
    decline_queues = Queue.objects.filter(
        uid=uid,
        community=community,
        state=Queue.DECLINE
    )
    # if a request was declined in the past, check its creation
    # datetime
    if decline_queues:
        latest_q = (
            decline_queues.latest('version_end_date') or
            decline_queues.latest('version_start_date')
        )
        logger.debug(f"{latest_q=}")
        latest_start_dt: Optional[datetime] = getattr(
            latest_q,
            'version_start_date',
            None
        )
        latest_end_dt: Optional[datetime] = getattr(
            latest_q,
            'version_end_date',
            None
        )
        latest_dt: datetime = latest_start_dt or latest_end_dt 
        backoff_hours = community.follow_request_backoff # hours
        if not backoff_hours:
            return
        backoff_seconds = backoff_hours * 60 * 60
        delta = datetime.now(pytz.utc) - latest_dt
        delta_seconds = delta.total_seconds()
        logger.debug(f"{delta_seconds=}")

        if delta_seconds < backoff_seconds:
            return True

""" Return True if we should back-off from creating a new Queue
    because a Queue object for this community / user pair was recently created
    or deleted. 
"""
def backoff(community, uid):
    queues = Queue.objects.filter(
                uid=uid,
                community=community,
    )
    if not queues:
        return
    latest_start_q: Optional[Queue] = queues.latest('version_start_date')
    latest_end_q: Optional[Queue] = queues.latest('version_end_date')
    latest_start_dt: Optional[datetime] = getattr(
        latest_start_q,
        'version_start_date',
        None
    )
    latest_end_dt: Optional[datetime] = getattr(
        latest_end_q,
        'version_end_date',
        None
    )
    latest = get_latest(
        latest_start_dt,
        latest_end_dt
    )
    if latest:
        backoff: int = community.request_queue_backoff * 60 # second
        delta = datetime.now(pytz.utc) - latest
        delta_seconds = delta.total_seconds()
        logger.debug(f"{delta_seconds=}")
        if delta_seconds < backoff:
            return True

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
            if backoff(community, uid):
                continue
            if decline_backoff(community, uid):
                continue
            if pending_request_exists(community, uid):
                continue
            if accept_request_exists(community, uid):
                continue
            create_queue(community, uid, bot_screen_name)

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
    followers = update_social_ids(
        user=userid,
        cached=False,
        bot_screen_name=username,
        relationship="followers"
    )
    if not followers:
        followers = update_social_ids(
            user=userid,
            cached=True,
            bot_screen_name=username,
            relationship="followers"
        )
    if followers and userid in followers:
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

@shared_task
def handle_update_request_queue():
    """Update queue state of follow requests

    Detect queues that were canceled by Twitter user or declined in the Twitter
    web API but whose state is still 'PENDING' and change state to 'CANCELED'.
    Detect queues that were accepted from Twitter web API but whose state is
    still 'PENDING' and change their state to 'ACCEPTED'.
    """
    protected_community_qs = Community.objects.filter(account__protected=True)
    for community in protected_community_qs:
        update_request_queue(community)