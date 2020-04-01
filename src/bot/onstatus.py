import logging
import tweepy

from bot.doctoctocbot import (
    community_retweet,
    isreplacement,
    isquote,
    has_retweet_hashtag,
)
from bot.lib.statusdb import Addstatus
from bot.tweepy_api import get_api
from conversation.models import create_tree, Tweetdj
from moderation.moderate import process_unknown_user



logger = logging.getLogger(__name__)

def triage(statusid):
    try:
        api = get_api()
        status = api.get_status(statusid, tweet_mode='extended')
    except tweepy.TweepError as e:
        logger.error(e)
        return
        
    sjson = status._json
    logger.debug(f'extended status: {sjson["user"]["screen_name"]} {sjson["full_text"]}')

    dbstatus = Addstatus(sjson)
    dbstatus.addtweetdj()
    dbstatus.add_image()

    logger.info(f"2° has_retweet_hashtag(sjson): {bool(has_retweet_hashtag(sjson))}")
    logger.info(f"4° not ('retweeted_status' in sjson): {not ('retweeted_status' in sjson)}")

    create_tree(statusid)
    hrh = has_retweet_hashtag(sjson)
    userid = sjson['user']['id']
    if (
        not isreplacement(sjson)
        and hrh
    ):
        logger.info("Retweeting status %s: %s ", status.id, status.full_text)
        community_retweet(status.id, userid, hrh)

def triage_status(status_id):
    try:
        sjson = Tweetdj.objects.get(statusid=status_id).json
    except Tweetdj.DoesNotExist:
        triage(status_id)
        return
    hrh = has_retweet_hashtag(sjson)
    if (not isreplacement(sjson)
        and not isquote(sjson)
        and hrh):
        logger.info(
            "Sending status %s: %s to function community_retweet()",
            sjson["id"],
            sjson["full_text"]
        )
        community_retweet(sjson["id"], sjson["user"]["id"], hrh)
       
def triage_user(sjson):
    hrh = has_retweet_hashtag(sjson)
    if (hrh and not ('retweeted_status' in sjson)):
        process_unknown_user(sjson["user"]["id"], sjson["id"], hrh)
