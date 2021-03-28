import logging
import datetime
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

def socialuser(backend, user, response, *args, **kwargs):
    from .models import SocialUser, SocialMedia
    if backend.name == 'twitter':
        sm_mi, created1 = SocialMedia.objects.get_or_create(name=backend.name)
        logger.debug(f'socialmedia: {sm_mi}, created: {created1}')
        tuid_int = kwargs['uid']
        su_mi, created2 = SocialUser.objects.get_or_create(user_id=tuid_int, social_media=sm_mi)
        logger.debug(f'socialuser: {su_mi}, created: {created2}')
        return {'socialuser': su_mi}

def create_twitter_social_user(userid):
    try:
        twitter = SocialMedia.objects.get(name='twitter')
    except SocialMedia.DoesNotExist:
        logger.error('Twitter SocialMedia object does not exist.')
        return
    su, created = SocialUser.objects.get_or_create(user_id=userid, social_media=twitter)
    return su, created

def create_twitter_social_user_and_profile(userid):
    try:
        su, created = create_twitter_social_user(userid)
    except TypeError:
        return
    bot_screen_names = Account.objects \
        .filter(active=True) \
        .values_list("username", flat=True)
    bot_screen_name = random.choice(bot_screen_names)
    create_update_profile_twitter(su, bot_screen_name=bot_screen_name)
    return su, created
    
def user(backend, user, response, *args, **kwargs):
    from users.models import User
    if backend.name == 'twitter':
        logger.debug(f"user.socialuser {user.socialuser} {type(user.socialuser)}")
        if user.socialuser is None:
            user.socialuser = kwargs['socialuser']
            user.save()
        logger.debug(f'socialmedia: {user}')
        
def profile(backend, user, response, *args, **kwargs):
    if backend.name == 'twitter':
        logger.debug(f"user.socialuser {user.socialuser} type:{type(user.socialuser)}")
        try:
            p = user.socialuser.profile
            logger.debug(f"user.socialuser.profile {p} type:{type(p)}")
            p.json = response
            p.save()
            logger.debug(f"user.socialuser.profile {user.socialuser.profile} type:{type(user.socialuser.profile)}")
        except Profile.DoesNotExist:
            p = Profile.objects.create(json=response, socialuser=user.socialuser) 
            logger.debug(f"user.socialuser.profile {user.socialuser.profile} type:{type(user.socialuser.profile)}")
        
        avatar(p, response)

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

def create_update_profile_twitter(
        su: SocialUser,
        bot_screen_name=None,
        cache=False
    ):
    userid = su.user_id
    try:
        tweetdj_mi = Tweetdj.objects.filter(userid = userid).latest()
    except Tweetdj.DoesNotExist:
        tweetdj_mi = None
    if not tweetdj_mi or not tweetdj_mi.json.get("user") or not cache:
        userjson = getuser(
            userid,
            bot_screen_name=bot_screen_name
        )
    else:
        userjson = tweetdj_mi.json.get("user")
    twitterprofile(userjson)
    
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