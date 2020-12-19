import logging

from request.models import Queue
from community.models import Community
from request.twitter_request import get_incoming_friendship
from moderation.social import update_social_ids

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
