from typing import List
import tweepy
import logging
from bot.tweepy_api import get_api
from datetime import datetime, timezone
from bot.lib.statusdb import Addstatus
from community.helpers import (
    get_community_member_id,
    get_community_twitter_tweepy_api,
)
from conversation.models import TwitterUserTimeline

from django.db.utils import DatabaseError

logger = logging.getLogger(__name__)

def user_id_list_timeline(user_id_list: List):
    if not user_id_list:
        return
    api = get_api()
    for userid in user_id_list:
        try:
            get_user_timeline(userid, api)
        except tweepy.TweepError as e:
            logger.error(f"Tweepy Error: {e}")

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
    api_call = False
    first: bool = True
    high_statusid: int = 0
    try:
        since_id = TwitterUserTimeline.objects.get(userid=userid).statusid
    except TwitterUserTimeline.DoesNotExist:
        since_id = None
    logger.debug(f"{since_id=}")
    for status in tweepy.Cursor(api.user_timeline, 
                        user_id=userid, 
                        count=200,
                        since_id=since_id,
                        max_id=None,
                        trim_user=False,
                        exclude_replies=False,
                        include_rts=True,
                        tweet_mode="extended"
                        ).items():
        api_call = True
        if first:
            try:
                tut = TwitterUserTimeline.objects.get(userid=userid)
            except TwitterUserTimeline.DoesNotExist:
                try:
                    tut = TwitterUserTimeline.objects.create(userid=userid)
                except DatabaseError:
                    return
            first = False
        if status.id > high_statusid:
            high_statusid = status.id
        logger.debug(f"{high_statusid=}")
        logger.debug(f"{status._json=}")
        db = Addstatus(status._json)
        db.addtweetdj()
    # set TwitterUserTimeline statusid to the highest retrieved statusid
    logger.debug(f"{high_statusid=}")
    try:
        tut = TwitterUserTimeline.objects.get(userid=userid)
        tut.last_api_call = datetime.now(tz=timezone.utc)
        if not tut.statusid or tut.statusid < high_statusid:
            tut.statusid = high_statusid
            tut.statusid_updated_at = datetime.now(tz=timezone.utc)
        tut.save()
    except TwitterUserTimeline.DoesNotExist:
        return