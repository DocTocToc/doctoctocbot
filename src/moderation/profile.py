import logging
from typing import Optional
import datetime
import pytz
import json
from os.path import exists, basename
import requests
from urllib.parse import urlparse
import tweepy
import random
from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.db.utils import DatabaseError
from django.conf import settings
from django.utils import timezone
from moderation.models import SocialUser, Profile, SocialMedia
from conversation.models import Tweetdj
from bot.bin.user import getuser
from bot.tweepy_api import get_api
from community.models import Community
from bot.models import Account

logger = logging.getLogger('root')
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)

def create_twitter_social_user(userid):
    try:
        twitter = SocialMedia.objects.get(name='twitter')
    except SocialMedia.DoesNotExist:
        logger.error('Twitter SocialMedia object does not exist.')
        return None, None
    try:
        return SocialUser.objects.get_or_create(
            user_id=userid,
            social_media=twitter
        )
    except IntegrityError as e:
        logger.error(e)
        return None, None

def create_twitter_social_user_and_profile(
        userid,
        cache=False,
        community: Community=None,
    ):
    try:
        su, created = create_twitter_social_user(userid)
    except TypeError:
        return
    if not su:
        return
    bot_screen_names = []
    other_bots_sn = Account.objects \
        .filter(active=True) \
        .values_list("username", flat=True)
    if community:
        try:
            community_bot_screen_name = community.account.username
        except:
            logger.error(f'Set up a bot account for {community}')
            community_bot_screen_name = None
        if community_bot_screen_name:
            bot_screen_names.append(community_bot_screen_name)
        try:
            other_bots_sn.remove(community_bot_screen_name)
        except ValueError:
            pass
    bot_screen_names.extend(other_bots_sn)
    for bot_screen_name in bot_screen_names:
        if (
            create_update_profile_twitter(
                su,
                bot_screen_name=bot_screen_name,
                cache=cache
            )
        ):
            return su, created

def twitterprofile(jsn):
    if not jsn or not isinstance(jsn, dict):
        return
    user_id = jsn.get("id")
    if not user_id:
        return
    try:
        su = SocialUser.objects.get(user_id=jsn["id"])
    except SocialUser.DoesNotExist:
        try:
            sm, _ = SocialMedia.objects.get_or_create(name="twitter")
        except DatabaseError:
            return
        try:
            su, _ = SocialUser.objects.get_or_create(
                user_id=user_id,
                social_media = sm,
            )
        except DatabaseError:
            return
            
    if hasattr(su, 'profile'):
        p = Profile.objects.get(socialuser=su)
        p.json = jsn
        p.save()
    else:
        try:
            p = Profile.objects.create(socialuser=su, json=jsn)
        except IntegrityError as e:
            logger.debug(e)
            return
    avatar(p, jsn)
    return True
            
def avatar(profile, response):
    img_url = response.get("profile_image_url_https")
    name = urlparse(img_url).path.split('/')[-1]
    logger.debug(f"name (Twitter): {name}, name (Database): {profile.normalavatar.name.split('/')[-1]}")
    name_twitter_uid = name.split('_')[0]
    name_database_uid = profile.normalavatar.name.split('/')[-1].split('_')[0]
    logger.debug(f"uid (Twitter): {name_twitter_uid}, uid (Database): {name_database_uid}")
    if name_twitter_uid == name_database_uid:
        return
    save_profile_pictures(img_url, profile)

def save_profile_pictures(img_url, profile):
    name = urlparse(img_url).path.split('/')[-1]  
    resp = requests.get(img_url)
    if resp.status_code == 200:
        profile.normalavatar.delete(save=False)
        profile.normalavatar.save(name, ContentFile(resp.content), save=False)
        
    name = name.replace('_normal', '_bigger')
    resp = requests.get(img_url.replace('_normal', '_bigger'))
    
    if resp.status_code == 200:
        profile.biggeravatar.delete(save=False)
        profile.biggeravatar.save(name, ContentFile(resp.content), save=False)
        
    name = name.replace('_bigger', '_mini')
    resp = requests.get(img_url.replace('_normal', '_mini'))
    
    if resp.status_code == 200:
        profile.miniavatar.delete(save=False)
        profile.miniavatar.save(name, ContentFile(resp.content), save=False)
    
    profile.save()

def is_profile_uptodate(userid):    
    
    try:
        su = SocialUser.objects.get(user_id=userid)
    except SocialUser.DoesNotExist:
        return
        
    if hasattr(su, "profile"):
        td = datetime.timedelta(days=settings.PROFILE_TIMEDELTA_DAYS)
        if (datetime.datetime.now(datetime.timezone.utc) - su.profile.updated) < td:
            return True
    else:
        return False
    
def screen_name(userid):
    try:
        su = SocialUser.objects.get(user_id=userid)
    except SocialUser.DoesNotExist:
        return

    if hasattr(su, "profile"):
        return su.profile.screen_name_tag()

def check_profile_pictures(userid):
    """
    Check if profile pictures (normal, bigger, mini) are available.
    If not, try to download them again.
    If the link is down, update the profile.
    """
    try:
        su = SocialUser.objects.get(user_id=userid)
    except SocialUser.DoesNotExist:
        return
    if not hasattr(su, "profile"):
        return
    profile = su.profile
    for size in ["mini", "normal", "bigger"]:
        default = f"default_profile_{size}.png"
        attr = f"{size}avatar"
        try:
            path = getattr(profile, attr).path
            if (basename(path) == default) or (not exists(path)):
                logger.info(f"Update profile pictures of {profile.screen_name_tag()}")
                update_profile_pictures(su)
        except AttributeError:
            pass
    
def update_profile_pictures(socialuser):
    try:
        profile = socialuser.profile
    except AttributeError:
        return
    if not profile:
        return
    last_tweet = Tweetdj.objects.filter(socialuser=socialuser).latest()
    if not last_tweet:
        return
    user = last_tweet.json.get("user", None)
    if user:
        img_url = user.get("profile_image_url_https", None)
        if img_url:
            save_profile_pictures(img_url, profile)

def create_update_profile(userid, bot_screen_name):
    try:
        su: SocialUser = SocialUser.objects.get(user_id=userid)
    except SocialUser.DoesNotExist:
        return
    try:
        sm: SocialMedia = su.social_media
    except AttributeError:
        return
    if sm.name == 'twitter':
        create_update_profile_twitter(
            su,
            bot_screen_name=bot_screen_name
        )
    elif sm.name == settings.THIS_SOCIAL_MEDIA:
        create_update_profile_local(su)

def create_update_profile_twitter(
        su: SocialUser,
        bot_screen_name=None,
        cache=False
    ):
    try:
        su.profile
        has_profile = True
    except Profile.DoesNotExist:
        has_profile = False
    if cache and has_profile:
        return True
    userid = su.user_id
    try:
        tweetdj_mi = Tweetdj.objects.filter(
            userid = userid,
            json__isnull=False
        ).latest()
    except Tweetdj.DoesNotExist:
        tweetdj_mi = None
    if not tweetdj_mi or not tweetdj_mi.json.get("user") or not cache:
        userjson = getuser(
            userid,
            bot_screen_name=bot_screen_name
        )
    else:
        userjson = tweetdj_mi.json.get("user")
    return twitterprofile(userjson)
    
def create_update_profile_local(su: SocialUser):
    try:
        username: str = su.user_set.first().username
    except:
        return
    profile = {"screen_name": username}
    try:
        Profile.objects.create(
            socialuser=su,
            json=json.loads(json.dumps(profile)),
        )
    except DatabaseError:
        return

def update_twitter_followers_profiles(community: Community):
    """Update Twitter profiles of all followers
    """
    if not isinstance(community, Community):
        logger.error(
            f"{community} is not an instance of the 'Community' class"
        )
        return
    try:
        screen_name = community.account.username
    except:
        logger.error(
            f"Could not retrieve username associated with {community}"
        )
        return
    try:
        api = get_api(community.account.username)
    except:
        return
    c = tweepy.Cursor(api.followers, screen_name=screen_name, count=200)
    for follower in c.items():
        logger.debug(f"{follower=}")
        twitterprofile(follower._json)

def recent_twitter_screen_name(user_id, bot_user_id, dtdelta):
    min_dt = datetime.datetime.min.replace(tzinfo=pytz.UTC)
    cutoff: datetime.datetime = timezone.now() - dtdelta
    # status
    tweetdj_qs = Tweetdj.objects.filter(userid=user_id)
    if tweetdj_qs:
        status_dt = tweetdj_qs.latest('statusid').created_at or min_dt 
    else:
        status_dt = min_dt
    # profile
    profile_qs = Profile.objects.filter(json__id=user_id)
    if profile_qs:
        profile_dt = profile_qs.latest('id').updated
    else:
        profile_dt = min_dt
    logger.debug(f'{status_dt=} {profile_dt=}')
    if status_dt > profile_dt and status_dt > cutoff:
        logger.debug(f'{tweetdj_qs.latest("statusid")=}')
        return tweetdj_qs.latest('statusid').json["user"]["screen_name"]
    elif profile_dt > status_dt and profile_dt > cutoff:
        logger.debug(f'{profile_qs.latest("id")=}')
        return profile_qs.latest('id').json["screen_name"]
    else:
        try:
            bot_screen_name = Account.objects.get(userid=bot_user_id).username
        except Account.DoesNotExist as e:
            logger.error(e)
            return
        try:
            su=SocialUser.objects.get(user_id=user_id)
        except SocialUser.DoesNotExist as e:
            logger.error(e)
            return
        create_update_profile_twitter(
            su,
            bot_screen_name=bot_screen_name,
            cache=False
        )
        profile = Profile.objects.get(socialuser=su)
        return profile.screen_name_tag()