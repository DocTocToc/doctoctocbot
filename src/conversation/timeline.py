from typing import List
import tweepy
import logging
from bot.tweepy_api import get_api
from datetime import datetime, timezone
from community.helpers import (
    get_community_member_id,
    get_community_twitter_tweepy_api,
)
from conversation.models import TwitterUserTimeline

from django.db.utils import DatabaseError
from django.db import transaction


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

def get_user_timeline(userid, api, force=False):
    from bot.lib.statusdb import Addstatus
    first: bool = True
    high_statusid: int = 0
    try:
        tut_last=TwitterUserTimeline.objects.filter(userid=userid).last()
    except TwitterUserTimeline.DoesNotExist:
        tut_last=None
    if force:
        since_id=None
    else:
        try:
            since_id = tut_last.statusid
        except AttributeError:
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
        if first:
            with transaction.atomic():
                try:
                    tut = TwitterUserTimeline.objects.get(userid=userid)
                except TwitterUserTimeline.DoesNotExist:
                    try:
                        tut = TwitterUserTimeline.objects.create(userid=userid)
                    except DatabaseError:
                        return
                except TwitterUserTimeline.MultipleObjectsReturned:
                    # TwitterUserTimeline objects should be unique for each userid
                    # Table got corrupted. This code tries to fix it.
                    tuts = TwitterUserTimeline.objects.filter(userid=userid)
                    tut_first = tuts.first()
                    tut_last = tuts.last()
                    created_at = tut_first.created_at
                    tut_last.created_at = created_at
                    tut_last.save()
                    for tut in tuts:
                        if tut.id == tut_last.id:
                            # keep the last object that we just updated
                            continue
                        tut.delete()
                first = False
        if status.id > high_statusid:
            high_statusid = status.id
        db = Addstatus(status._json)
        db.addtweetdj()
    # set TwitterUserTimeline statusid to the highest retrieved statusid
    logger.debug(f"{high_statusid=}")
    with transaction.atomic():
        try:
            tut = TwitterUserTimeline.objects.get(userid=userid)
            tut.last_api_call = datetime.now(tz=timezone.utc)
            if not tut.statusid or tut.statusid < high_statusid:
                tut.statusid = high_statusid
                tut.statusid_updated_at = datetime.now(tz=timezone.utc)
            tut.save()
        except TwitterUserTimeline.MultipleObjectsReturned:
            # TwitterUserTimeline objects should be unique for each userid
            # Table got corrupted. This code tries to fix it.
            tuts = TwitterUserTimeline.objects.filter(userid=userid)
            tut_first = tuts.first()
            tut_last = tuts.last()
            created_at = tut_first.created_at
            tut_last.created_at = created_at
            tut_last.last_api_call = datetime.now(tz=timezone.utc)
            if not tut_last.statusid or tut_last.statusid < high_statusid:
                tut_last.statusid = high_statusid
                tut_last.statusid_updated_at = datetime.now(tz=timezone.utc)
            tut_last.save()
            for tut in tuts:
                if tut.id == tut_last.id:
                    # keep the last object that we just updated
                    continue
                tut.delete()
        except TwitterUserTimeline.DoesNotExist:
            return