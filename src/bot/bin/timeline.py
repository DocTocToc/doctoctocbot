from typing import List

from community.models import Community
from bot.tweepy_api import get_api
from bot.lib.statusdb import Addstatus
from timeline.models import add_status_tl, Status
import tweepy
import logging

logger = logging.getLogger(__name__)

def record_timeline():
    for community in Community.objects.filter(active=True):
        su = community.account.socialuser
        if not su:
            continue
        record_user_timeline(
            su.user_id,
            count=200,
            force=False,
            retweeted=True
        )
        
def record_user_timeline(user_id, count=200, force=False, retweeted=False):
    """
    Send requests to record user timeline as long as not all tweets during one
    request already exist in database.
    retweeted: bool If status is a retweet, add retweeted status to database
    """
    max_statusid = None
    api=get_api()
    new_tweets = True
    while new_tweets:
        if not force:
            new_tweets = False
        try:
            status_lst = api.user_timeline(
                user_id=user_id,
                count=count,
                max_id=max_statusid,
                tweet_mode="extended",
                include_rts=True
            )
            if not status_lst:
                logger.warn("request is empty")
                break
            for status in status_lst:
                dbstatus = Addstatus(status._json)
                tweetdj, created = dbstatus.addtweetdj(update=True)
                if retweeted and tweetdj.retweetedstatus:
                    dbstatus = Addstatus(status._json["retweeted_status"])
                    dbstatus.addtweetdj(update=True)
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