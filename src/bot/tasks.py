import logging
import time
from typing import Optional
from django.conf import settings
from constance import config
from celery import shared_task

from bot.bin.friendship import create_friendship
from bot.lib.status import status_json_log
from bot.models import Account
from community.models import Community
from moderation.models import Follower, Friend, SocialUser
from moderation.profile import (
    create_twitter_social_user,
    create_update_profile_twitter
)
from moderation.social import update_social_ids
from bot.follow import Follow
from bot.unfollow import Unfollow
from moderation.social import get_socialuser_from_screen_name
from django.core.management.base import BaseCommand, CommandError
from moderation.profile import create_twitter_social_user_and_profile
from moderation.models import SocialUser, Category, UserCategoryRelationship
from tweepy.error import TweepError
from django.db.utils import DatabaseError

logger = logging.getLogger(__name__)

@shared_task
def handle_retweetroot(statusid: int, bot_screen_name: str):
    from .bin.thread import retweetroot
    retweetroot(statusid,bot_screen_name)

@shared_task
def handle_question(statusid: int, bot_screen_name: str):
    from bot.bin.thread import question_api
    for i in range(1,8):
        logger.info(
            f"handle_question {statusid=} {bot_screen_name=}, loop: {i}"
        )
        ok = question_api(statusid, bot_screen_name)
        if ok:
            break
        else:
            time.sleep(30*2**i)



@shared_task
def handle_triage_status(status_id: int, community: str):
    from bot.onstatus import triage_status

    try:
        community = Community.objects.get(name=community)
    except Community.DoesNotExist:
        return
    triage_status(status_id, community)



@shared_task
def handle_create_friendship(userid, communityid):
    try:
        community = Community.objects.get(id=communityid)
    except Community.DoesNotExist:
        return
    create_friendship(userid, community)

def update_network(user_id, bot_screen_name, relationship):
    try:
        su = SocialUser.objects.get(user_id=user_id)
    except SocialUser.DoesNotExist:
        return
    update_social_ids(
        su,
        cached=False,
        bot_screen_name=bot_screen_name,
        relationship=relationship,
    )

@shared_task
def handle_add_followers_to_socialusers():
    exist_ids = list(SocialUser.objects.values_list("user_id", flat=True))
    for account in Account.objects.filter(active=True):
        try:
            _su = SocialUser.objects.get(user_id=account.userid)
        except SocialUser.DoesNotExist:
            continue
        update_network(_su.user_id, account.username, 'followers')
        try:
            follower_ids = Follower.objects.filter(user=_su).latest().id_list
        except Follower.DoesNotExist:
            continue
        new_ids = [uid for uid in follower_ids if uid not in exist_ids]
        for userid in new_ids:
            su, created = create_twitter_social_user(userid)
            if su and created:
                create_update_profile_twitter(
                    su,
                    account.username,
                    cache=True
                )

@shared_task
def handle_add_friends_to_socialusers():
    exist_ids = list(SocialUser.objects.values_list("user_id", flat=True))
    for account in Account.objects.filter(active=True):
        try:
            su = SocialUser.objects.get(user_id=account.userid)
        except SocialUser.DoesNotExist:
            continue
        update_network(su.user_id, account.username, 'friends')
        try:
            friend_ids = Friend.objects.filter(user=su).latest().id_list
        except Friend.DoesNotExist:
            continue
        new_ids = [uid for uid in friend_ids if uid not in exist_ids]
        for userid in new_ids:
            su, created = create_twitter_social_user(userid)
            if su and created:
                create_update_profile_twitter(
                    su,
                    account.username,
                    cache=True
                )

@shared_task
def update_bots_followers():
    for account in Account.objects.filter(active=True):
        try:
            su = SocialUser.objects.get(user_id=account.userid)
        except SocialUser.DoesNotExist:
            continue
        update_social_ids(
            su,
            cached=False,
            bot_screen_name=account.username,
            relationship='followers',
        )
        try:
            period = settings.API_FOLLOWERS_PERIOD
            time.sleep(period)
        except AttributeError:
            logger.error(f"API_FOLLOWERS_PERIOD is not set.")
            pass

@shared_task
def update_bots_friends():
    for account in Account.objects.filter(active=True):
        try:
            su = SocialUser.objects.get(user_id=account.userid)
        except SocialUser.DoesNotExist:
            continue
        update_social_ids(
            su,
            cached=True,
            bot_screen_name=account.username,
            relationship='friends',
        )
        try:
            period = settings.API_FRIENDS_PERIOD
            time.sleep(period)
        except AttributeError:
            logger.error(f"API_FRIENDS_PERIOD is not set.")
            pass

@shared_task(
    soft_time_limit=config.bot_follow_soft_time_limit,
    time_limit=config.bot_follow_time_limit
)
def follow(
        screen_name: str,
        count: int,
        days: int,
        sample_size: Optional[int] = None,
        force: bool = False,
        sleep: Optional[int] = None
    ):
        """Create friendships based on categories and prospects"""
        socialuser = get_socialuser_from_screen_name(screen_name)
        if not socialuser:
            logger.ERROR(
                'No SocialUser found for screen_name "%s"' % screen_name
            )
            return
        if count is None or count > 20 or count < 0:
            logger.ERROR(
                'count is %s, it should be a positive integer <= 20' % count
            )
            return
        follow = Follow(
            socialuser=socialuser,
            count=count,
            delta=days,
            force=force,
            sample_size=sample_size,
            sleep=sleep
        )
        return follow.process()


@shared_task(
    soft_time_limit=config.bot_unfollow_soft_time_limit,
    time_limit=config.bot_unfollow_time_limit
)
def unfollow(
        screen_name: str,
        count: int,
        days: int,
        sample_size: Optional[int] = None,
        force: bool = False,
        sleep: Optional[int] = None,
    ):
        """Destroy friendships"""
        socialuser = get_socialuser_from_screen_name(screen_name)
        if not socialuser:
            logger.ERROR(
                'No SocialUser found for screen_name "%s"' % screen_name
            )
            return
        if count is None or count > 40 or count < 0:
            logger.ERROR(
                'count is %s, it should be a positive integer <= 40' % count
            )
            return
        unfollow = Unfollow(
            socialuser=socialuser,
            count=count,
            delta=days,
            force=force,
            sample_size=sample_size,
            sleep=sleep,
        )
        return unfollow.process()

@shared_task()
def search(community: Optional[str] = None):
    from bot.tweepy_api import get_api
    from bot.bin.search import retweet_recent

    if not community:
        return
    try:
        community_mi = Community.objects.get(name=community)
    except Community.DoesNotExist:
        return
    try:
        username = community_mi.account.username
    except:
        return
    try:
        api = get_api(username=username)
    except:
        return
    track_list = []
    try:
        hashtags = Community.objects.get(name=community).hashtag.all()
    except Community.DoesNotExist:
        return
    if not hashtags:
        return
    for hashtag in hashtags:
        track_list.append(f"#{hashtag}")
    # search for and process recent tweets containing this community's hashtags
    retweet_recent(track_list, community, api)

@shared_task
def handle_on_status(json: dict, community: str):
    from bot.onstatus import triage
    logger.info(
        f"handling status {status_json_log(json)} for community {community}"
    )
    triage(json=json, community=community)