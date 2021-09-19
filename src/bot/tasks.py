import logging
import requests
import time
from pathlib import Path

from django.conf import settings
from celery import shared_task

from bot.bin.friendship import create_friendship
from bot.models import Account
from community.models import Community
from moderation.models import Follower, Friend, SocialUser
from moderation.profile import (
    create_twitter_social_user,
    create_update_profile_twitter
)
from moderation.social import update_social_ids

logger = logging.getLogger(__name__)

@shared_task
def handle_retweetroot(statusid: int):
    from .bin.thread import retweetroot
    retweetroot(statusid)
    
@shared_task
def handle_question(statusid: int):
    from bot.bin.thread import question_api
    for i in range(1,8):
        logger.info(f"handle_question statusid: {statusid}, loop: {i}")
        ok = question_api(statusid)
        if ok:
            break
        else:
            time.sleep(30*2**i)

@shared_task
def handle_on_status(json: dict, community: str):
    from bot.onstatus import triage
    logger.info(f"handling status {json} for community {community}")
    triage(json=json, community=community)
    
@shared_task
def handle_image(url, filename):
    for name in ["thumb", "large"]:
        if name == "thumb":
            filepath = settings.BOT_IMAGES_THUMBNAILS_PATH + "/" + filename
        elif name == "large":
            filepath = settings.BOT_IMAGES_PATH + "/" + filename
        full_url = url + f"?name={name}"
        r = requests.get(full_url, allow_redirects=True)
        with open(filepath, 'wb') as f:
            f.write(r.content)
        file = Path(filepath)
        if file.is_file():
            logger.debug(f"{name} image %s written on disk." % filepath)
        else:
            logger.error(f"{name} image %s not found on disk." % filepath)
     
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
            cached=True,
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