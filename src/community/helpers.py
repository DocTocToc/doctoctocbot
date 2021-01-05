import logging
from typing import Optional
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from django.db.utils import DatabaseError
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import activate
from community.models import Community
from moderation.models import SocialUser
from bot.tweepy_api import get_api

logger = logging.getLogger(__name__)

def get_community(request):
    """
    Return a Community object or None given the request.
    """
    site = get_current_site(request)
    if not site:
        return
    try:
        return Community.objects.get(site=site.id)
    except DatabaseError:
        return
    except Community.DoesNotExist:
        try:
            site = Site.objects.first()
            if site:
                return Community.objects.get(site=site.id)
        except Community.DoesNotExist as e:
            logger.warn("Create at least one community. %s", e)
            
def site_url(community):
    if not community:
        return
    if settings.DEBUG:
        protocol="http://"
    else:
        protocol="https://"
    return mark_safe(f"{protocol}{community.site.domain}")

def activate_language(community):
    if not community:
        return
    if not isinstance(community, Community):
        return
    language = community.language
    if not language:
        return
    activate(language)
    
    
def get_community_twitter_tweepy_api(community, backend=False):
    if not community:
        return
    if not isinstance(community, Community):
        return
    return get_api(community.account.username, backend)
    
def get_community_bot_socialuser(community: Community) -> Optional[SocialUser]:
    if not community:
        return
    if not isinstance(community, Community):
        return
    try:
        user_id = community.account.userid
    except AttributeError:
        return
    try:
        su = SocialUser.objects.get(user_id=user_id)
    except SocialUser.DoesNotExist:
        return
    return su

def get_community_bot_screen_name(community: Community) -> Optional[str]:
    if not community:
        return
    if not isinstance(community, Community):
        return
    try:
        screen_name = community.account.username
    except AttributeError:
        return
    return screen_name