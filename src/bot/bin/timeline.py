from typing import List

from community.models import Community
from bot.tweepy_api import get_api
from bot.lib.statusdb import Addstatus
from timeline.models import add_status_tl, Status
import tweepy
import logging

logger = logging.getLogger(__name__)

def get_timeline_with_rts(screen_name):
    API = get_api(username=screen_name, backend=True)
    try:
        return API.user_timeline(
            include_rts=True,
            count=200
        )
    except AttributeError:
        return

def record_timeline():
    for community in Community.objects.filter(active=True):
        status_lst = get_timeline_with_rts(community.account.username)
        if status_lst:
            for status in status_lst:
                add_status_tl(status, community)
        
        
def record_user_timeline(user_id, count=200, force=False):
    """
    Send requests to record user timeline as long as not all tweets during one
    request already exist in database.
    """
    max_statusid = None
    api=get_api()
    new_tweets = True
    while new_tweets:
        if not force:
            new_tweets = False
        try:
            status_lst = api.user_timeline(user_id=user_id, count=count, max_id=max_statusid, tweet_mode="extended")
            if not status_lst:
                logger.warn("request is empty")
                break
            for status in status_lst:
                dbstatus = Addstatus(status._json)
                created = dbstatus.addtweetdj()
                statusid = status._json["id"]
                if max_statusid is None:
                    max_statusid = statusid
                elif statusid < max_statusid:
                    max_statusid = statusid
                if created:
                    if not force:
                        new_tweets = True
        except tweepy.TweepError as e:
            logger.debug(e.response.text)
            break
        except tweepy.RateLimitError as e:
            logger.debug(e.response.text)
        except AttributeError:
            return
        max_statusid -= 1
            
def get_timeline_id_lst(n=None) -> List:
    """
    Return n last tweet from timeline as a list of statusid, excluding replies
    """
    return [status.statusid
            for status
            in Status.objects.all().filter(json__contains={'in_reply_to_status_id': None})][:n]