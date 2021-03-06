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


def get_status(statusid: int, community: Community):
    username = community.account.username
    api = get_api(username=username, backend=True)
    if not api:
        return
    try:
        return api.get_status(statusid, tweet_mode='extended')
    except tweepy.TweepError as e:
        logger.error(e)

def get_status_communities(statusid, community):
    for c in Community.objects.filter(active=True).remove(community):
        status = get_status(statusid=statusid, community=c)
        if status:
            return status

def triage(json: dict, community: str):
    # get community or communities managing the hashtags
    try:
        community = Community.objects.get(name=community)
    except Community.DoesNotExist:
        return
    status = get_status(json["id"], community)
    if not status:
        status = get_status_communities(json["id"], community)
    if not status:
        logger.warn(f'We could not get status {json["id"]}.')
        return
    sjson = status._json
    logger.debug(f'extended status: {sjson["user"]["screen_name"]} {sjson["full_text"]}')

    dbstatus = Addstatus(sjson)
    dbstatus.addtweetdj()
    dbstatus.add_image()
    hrh = has_retweet_hashtag(sjson)
    logger.debug(f"2° has_retweet_hashtag(sjson): {bool(hrh)}")
    logger.debug(f"4° not ('retweeted_status' in sjson): {not ('retweeted_status' in sjson)}")

    userid = sjson['user']['id']
    if hrh:
        create_tree_except_rt(status.id)
        community_retweet(status.id, userid, hrh)

def triage_status(status_id, community):
    try:
        tweetdj = Tweetdj.objects.get(statusid=status_id)
        sjson = tweetdj.json
    except Tweetdj.DoesNotExist:
        status = get_status(status_id, community)
        if not status:
            status = get_status_communities(status_id, community)
        if not status:
            return
        sjson = status._json
    hrh = has_retweet_hashtag(sjson)
    if hrh:
        logger.info(
            "Sending status %s: %s to function community_retweet()",
            sjson["id"],
            sjson["full_text"]
        )
        community_retweet(sjson["id"], sjson["user"]["id"], hrh)
