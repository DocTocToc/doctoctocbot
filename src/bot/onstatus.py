import logging
import tweepy

from bot.doctoctocbot import (
    community_retweet,
    has_retweet_hashtag,
    create_tree_except_rt
)
from bot.lib.statusdb import Addstatus
from bot.tweepy_api import get_api
from conversation.models import Tweetdj
from conversation.models import Hashtag
from community.models import Community

logger = logging.getLogger(__name__)

def get_status(statusid, communities):
    for community in communities:
        username = community.account.username
        api = get_api(username=username)
        if not api:
            continue
        try:
            return api.get_status(statusid, tweet_mode='extended')
        except tweepy.TweepError as e:
            logger.error(e)

def triage(jsn: dict):
    # get community or communities managing the hashtags
    hashtags = [h["text"] for h in jsn["entities"]["hashtags"]]
    logger.debug(f"{hashtags=}")
    if not hashtags:
        return
    hashtags_mi = []
    for h in hashtags:
        try:
            h_mi = Hashtag.objects.get(hashtag=h)
            hashtags_mi.append(h_mi)
        except Hashtag.DoesNotExist:
            continue
    communities = Community.objects.filter(hashtag__in=hashtags_mi)
    status = get_status(jsn["id"], communities)
    if not status:
        logger.warn(f'We could not get status {jsn["id"]}.')
        return
    sjson = status._json
    logger.debug(f'extended status: {sjson["user"]["screen_name"]} {sjson["full_text"]}')

    dbstatus = Addstatus(sjson)
    dbstatus.addtweetdj()
    dbstatus.add_image()

    logger.info(f"2° has_retweet_hashtag(sjson): {bool(has_retweet_hashtag(sjson))}")
    logger.info(f"4° not ('retweeted_status' in sjson): {not ('retweeted_status' in sjson)}")

    hrh = has_retweet_hashtag(sjson)
    userid = sjson['user']['id']
    if hrh:
        create_tree_except_rt(status.id)
        community_retweet(status.id, userid, hrh)

def triage_status(status_id):
    try:
        sjson = Tweetdj.objects.get(statusid=status_id).json
    except Tweetdj.DoesNotExist:
        triage(status_id)
        return
    hrh = has_retweet_hashtag(sjson)
    if hrh:
        logger.info(
            "Sending status %s: %s to function community_retweet()",
            sjson["id"],
            sjson["full_text"]
        )
        community_retweet(sjson["id"], sjson["user"]["id"], hrh)
