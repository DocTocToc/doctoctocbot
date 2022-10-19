import logging
import tweepy

from bot.doctoctocbot import (
    community_retweet,
    has_retweet_hashtag,
    create_tree_except_rt
)
from bot.lib.statusdb import Addstatus
from bot.addstatusdj import addstatus
from bot.tweepy_api import get_api, get_v1_v2
from conversation.models import Tweetdj
from conversation.models import Hashtag
from community.models import Community
from bot.tasks import handle_triage_status
from community.models import Community, Retweet

logger = logging.getLogger(__name__)


def get_status(statusid: int, community: Community):
    username = community.account.username
    api = get_api(username=username)
    if not api:
        return
    try:
        return api.get_status(statusid, tweet_mode='extended')
    except tweepy.TweepError as e:
        logger.error(e)

def get_status_communities(statusid, community):
    """Get a status through the account of another community
    Try to get a status through another account if the bot of a community was
    blocked by the author of the status.
    """
    for c in Community.objects.filter(active=True).exclude(id=community.id):
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
    tweetdj, created = dbstatus.addtweetdj()
    # handle non hydrated Tweetdj objects with null json field
    if tweetdj and not created and not tweetdj.json:
        dbstatus.addtweetdj(update=True)
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
        bot_username=community.account.username
    except:
        bot_username=None
    try:
        tweetdj = Tweetdj.objects.get(statusid=status_id)
        sjson = tweetdj.json
    except Tweetdj.DoesNotExist:
        tweetdj = addstatus(status_id, bot_username=bot_username)
        if tweetdj:
            sjson = tweetdj.json
        else:
            return
    try:
        hrh = has_retweet_hashtag(sjson)
    except TypeError:
        tweetdj = addstatus(status_id, bot_username=bot_username)
        hrh = has_retweet_hashtag(tweetdj.json)
    if hrh:
        community_retweet(status_id, tweetdj.json["user"]["id"], hrh)

def search_triage(community: Community):
    hashtags = list(
        Retweet.objects
        .filter(community=community)
        .order_by('hashtag')
        .values_list("hashtag__hashtag", flat=True)
        .distinct()
    )
    hashtags = [f'#{h}' for h in hashtags]
    search_string = " OR ".join(hashtags)
    logger.debug("search_string: %s" % (search_string))
    v1, v2 = get_v1_v2()
    if community.account.app.api == v1:
        api = get_api(username=community.account.username, mt=True)
        tweets = api.search_tweets(
            search_string,
            count=100,
            result_type="recent",
        )
        for tweet in tweets:
            logger.debug(f'{tweet.id} {tweet.text}')
            handle_triage_status.apply_async(
                kwargs={"status_id": tweet.id, "community": community.name}
            )
    elif community.account.app.api == v2:
        Client = get_api(username=community.account.username)
        tweets = Client.search_recent_tweets(
            search_string,
            max_results=100,
        )
        data, _includes, _errors, _meta = tweets
        for tweet in data:
            logger.debug(f'{tweet.id} {tweet.text}')
            handle_triage_status.apply_async(
                kwargs={"status_id": tweet.id, "community": community.name}
            )
        else:
            return