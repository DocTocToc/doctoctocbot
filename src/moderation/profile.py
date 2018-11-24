import logging
from django.core.exceptions import ObjectDoesNotExist
from psycopg2._json import json
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
    
def user(backend, user, response, *args, **kwargs):
    from .models import Profile
    from users.models import User
    if backend.name == 'twitter':
        logger.debug(f"user.socialuser {user.socialuser} {type(user.socialuser)}")
        if user.socialuser is None:
            user.socialuser = kwargs['socialuser']
            user.save()
        logger.debug(f'socialmedia: {user}')
        
def profile(backend, user, response, *args, **kwargs):
    from .models import Profile

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

def twitterprofile(json):
    from .models import SocialUser, Profile, SocialMedia
    try:
        su = SocialUser.objects.get(user_id = json["id"])
    except SocialUser.DoesNotExist:
        sm, _ = SocialMedia.objects.get_or_create(name="twitter")
        su = SocialUser.objects.create(user_id = json["id"],
                                       social_media = sm 
                                       )
    if hasattr(su, 'profile'):
        p = su.profile
        p.json = json
        p.save()
    else:
        p = Profile.objects.create(json=json, socialuser=su)
    
    avatar(p, json)
            
def avatar(profile, response):
    import requests
    from django.core.files.base import ContentFile
    from urllib.parse import urlparse
    
    img_url = response["profile_image_url_https"]
    name = urlparse(img_url).path.split('/')[-1]
    logger.debug(f"name (Twitter): {name}, name (Database): {profile.normalavatar.name.split('/')[-1]}")
    #if name == profile.normalavatar.name.split('/')[-1]:
    #    return
    
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