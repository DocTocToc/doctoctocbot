import tweepy
import logging
from bot.lib.statusdb import Addstatus
from community.helpers import (
    get_community_member_id,
    get_community_twitter_tweepy_api,
)

logger = logging.getLogger(__name__)

def community_timeline(community):
    userids = get_community_member_id(community)
    if not userids:
        return
    api = get_community_twitter_tweepy_api(community, backend=True)
    for userid in userids:
        try:
            get_user_timeline(userid, api)
        except tweepy.TweepError as e:
            logger.error(f"Tweepy Error: {e}")

def get_user_timeline(userid, api):
    for status in tweepy.Cursor(api.user_timeline, 
                        user_id=userid, 
                        count=200,
                        since_id=None,
                        max_id=None,
                        trim_user=False,
                        exclude_replies=False,
                        include_rts=True,
                        ).items():
        logger.debug(f"{status._json=}")
        db = Addstatus(status._json)
        db.addtweetdj()