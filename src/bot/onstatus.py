import logging
import tweepy

from django.db.utils import DatabaseError

from bot.twitter import getAuth
from bot.lib.statusdb import Addstatus
from moderation.moderate import addtoqueue
from bot.doctoctocbot import okrt, okrules, retweet, isknown, isauthorized, has_retweet_hashtag
from conversation.models import Treedj

logger = logging.getLogger(__name__)

def triage(statusid):
    status = tweepy.API(getAuth()).get_status(statusid, tweet_mode='extended')
    sjson = status._json
    logger.debug(f'extended status: {sjson["user"]["screen_name"]} {sjson["full_text"]}')

    dbstatus = Addstatus(sjson)
    dbstatus.addstatus()
    dbstatus.addtweetdj()

    if not isknown(sjson):
        addtoqueue(sjson)
    elif okrules(sjson):
        try:
            Treedj.objects.create(statusid=statusid)
        except DatabaseError as e:
            logger.error(str(e))
        if has_retweet_hashtag(sjson) and isauthorized(sjson):
            logger.info("Retweeting status %s: %s ", status.id, status.full_text)
            retweet(status.id)