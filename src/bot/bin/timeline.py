from typing import List

from community.models import Community
from bot.tweepy_api import get_api
from bot.lib.statusdb import Addstatus
from timeline.models import add_status_tl, Status
import tweepy
import logging
from conversation.timeline import get_user_timeline
from community.helpers import get_community_twitter_tweepy_api

logger = logging.getLogger(__name__)

def record_timeline():
    """Record bot timeline of active communities
    """
    for community in Community.objects.filter(active=True):
        su = community.account.socialuser
        if not su:
            continue
        api = get_community_twitter_tweepy_api(community)
        if not api:
            continue
        get_user_timeline(
            userid=su.user_id,
            api=api,
            force=False
        )
            
def get_timeline_id_lst(n=None) -> List:
    """
    Return n last tweet from timeline as a list of statusid, excluding replies
    """
    return [status.statusid
            for status
            in Status.objects.all().filter(json__contains={'in_reply_to_status_id': None})][:n]