import logging
import tweepy

from bot.doctoctocbot import (
    is_following_rules,
    retweet,
    isknown,
    has_greenlight,
    has_retweet_hashtag,
    isselfstatus,
    is_follower
)
from bot.lib.statusdb import Addstatus
from bot.twitter import getAuth
from conversation.models import create_tree, Tweetdj
from moderation.moderate import process_unknown_user



logger = logging.getLogger(__name__)

def triage(statusid):
    status = tweepy.API(getAuth()).get_status(statusid, tweet_mode='extended')
    sjson = status._json
    logger.debug(f'extended status: {sjson["user"]["screen_name"]} {sjson["full_text"]}')

    dbstatus = Addstatus(sjson)
    dbstatus.addtweetdj()
    dbstatus.add_image()

    logger.info(f"1° not isknown(sjson): {not isknown(sjson)}")
    logger.info(f"2° has_retweet_hashtag(sjson): {has_retweet_hashtag(sjson)}")
    logger.info(f"3° isselfstatus(sjson) {isselfstatus(sjson)}")
    logger.info(f"4° not ('retweeted_status' in sjson): {not ('retweeted_status' in sjson)}")

    if not isknown(sjson):
        triage_user(sjson)
    elif is_following_rules(sjson):
        create_tree(statusid)
        if (
            has_greenlight(sjson) and
            has_retweet_hashtag(sjson) and
            is_follower(sjson['user']['id'])    
        ):
            logger.info("Retweeting status %s: %s ", status.id, status.full_text)
            retweet(status.id)

def triage_status(status_id):
    try:
        sjson = Tweetdj.objects.get(statusid=status_id).json
    except Tweetdj.DoesNotExist:
        triage(status_id)
        return
    
    if (
        is_following_rules(sjson) and
        has_greenlight(sjson) and
        has_retweet_hashtag(sjson) and
        is_follower(sjson['user']['id'])
    ):
        logger.info("Retweeting status %s: %s ", sjson["id"], sjson["full_text"])
        retweet(sjson["id"])
       
def triage_user(sjson):
    if (has_retweet_hashtag(sjson) and
        not isselfstatus(sjson) and
        not ('retweeted_status' in sjson)):
        process_unknown_user(sjson["user"]["id"], sjson["id"])