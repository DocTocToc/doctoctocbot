from django.db.utils import DatabaseError
import logging
import tweepy

from bot.doctoctocbot import is_following_rules, retweet, isknown, \
    has_greenlight, has_retweet_hashtag, isselfstatus
from bot.lib.statusdb import Addstatus
from bot.twitter import getAuth
from conversation.models import create_tree
from moderation.moderate import addtoqueue


logger = logging.getLogger(__name__)

def triage(statusid):
    status = tweepy.API(getAuth()).get_status(statusid, tweet_mode='extended')
    sjson = status._json
    logger.debug(f'extended status: {sjson["user"]["screen_name"]} {sjson["full_text"]}')

    dbstatus = Addstatus(sjson)
    dbstatus.addtweetdj()
    dbstatus.add_image()

    if not isknown(sjson) \
        and has_retweet_hashtag(sjson) \
        and not isselfstatus(sjson) \
        and not 'retweeted_status' in sjson:
        
        addtoqueue(sjson)
    
    if is_following_rules(sjson):
        create_tree(statusid)
        if has_greenlight(sjson) and has_retweet_hashtag(sjson):
            logger.info("Retweeting status %s: %s ", status.id, status.full_text)
            retweet(status.id)