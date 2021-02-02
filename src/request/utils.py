import logging
from tweepy import TweepError
from request.models import Queue, RequestDm
from community.models import Community
from request.twitter_request import get_incoming_friendship
from moderation.social import update_social_ids
from community.helpers import get_community_twitter_tweepy_api

from django.db.utils import DatabaseError

logger = logging.getLogger(__name__) 

def accept_delete_queue(uid, community):
    state = Queue.ACCEPT
    delete_queue(uid, community, state)
    
def decline_delete_queue(uid, community):
    state = Queue.DECLINE
    delete_queue(uid, community, state)

def delete_queue(uid, community, state):
    for q in Queue.objects.current.filter(uid=uid,community=community):
        q = q.clone()
        q.state = state
        q.save()
        q.delete()

def update_request_queue(community: Community):
    """Update queue state of follow requests

    Detect queues that were canceled by Twitter user or declined in the Twitter
    web API but whose state is still 'PENDING' and change state to 'CANCELED'.
    Detect queues that were accepted from Twitter web API but whose state is
    still 'PENDING' and change their state to 'ACCEPTED'.
    """
    ifs = get_incoming_friendship(community)
    followers = update_social_ids(
        user = community.account.userid,
        cached = False,
        bot_screen_name = community.account.username,
        relationship = 'followers'
        )
    for q in Queue.objects.current.filter(state=Queue.PENDING):
        if q.uid in followers:
            q.state = Queue.ACCEPT
            q.save()
            q.delete()
        elif q.uid not in ifs:
            q.state = Queue.CANCEL
            q.save()
            q.delete()

def request_dm(queue):
    """Try to send a DM.
    Include instructions to self verify.
    """
    community = queue.community
    recipient_id = queue.uid
    text = community.twitter_request_dm_text
    if not text:
        return
    api = get_community_twitter_tweepy_api(community)
    try:
        rd = RequestDm.objects.create(queue=queue)
    except DatabaseError:
        return
    try:
        res = api.send_direct_message(
            recipient_id=recipient_id,
            text=text
        )
        rd.state = RequestDm.SENT
        rd.dm_id = res.id
        rd.save()
    except TweepError as e:
        logger.error(f"addstatus: Tweepy error: {e}")
        # code 150:
        # You cannot send messages to users who are not following you.
        # code 349
        # You cannot send messages to this user.
        error_code =  e.args[0][0]['code']
        rd.state = RequestDm.FAIL
        rd.error_code = error_code
        rd.save()


        
    