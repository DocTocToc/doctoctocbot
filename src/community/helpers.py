import logging
from typing import Optional, List
from collections import Counter
from django.core.cache import cache
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from django.db.utils import DatabaseError
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import activate
from community.models import Community, Trust
from bot.tweepy_api import get_api
from moderation.models import (
    UserCategoryRelationship,
    SocialMedia,
    SocialUser,
    Friend,
    Category
)

logger = logging.getLogger(__name__)

def get_community(request):
    """
    Return a Community object or None given the request.
    """
    site = get_current_site(request)
    if not site:
        return Community.objects.first()
    try:
        return Community.objects.get(site=site.id)
    except DatabaseError:
        return
    except Community.DoesNotExist:
        site = Site.objects.first()
        if site:
            try:
                return Community.objects.get(site=site.id)
            except Community.DoesNotExist as e:
                logger.warn("Create at least one community. %s", e)
        else:
            logger.warn("Create at least one Site. %s", e)
    
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
    
def get_community_twitter_tweepy_api(community):
    if not community:
        return
    if not isinstance(community, Community):
        return
    try:
        bot_screen_name = community.account.username
    except AttributeError:
        return
    return get_api(username=bot_screen_name)
    
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

def get_community_member_id(
        community,
        exclude_pending_follow_request=True
    ) -> Optional[List[int]]:
    if not community:
        return
    if not isinstance(community, Community):
        return
    categories = community.membership.all()
    try:
        twitter = SocialMedia.objects.get(name="twitter")
    except SocialMedia.DoesNotExist:
        return
    bot_social_user = get_community_bot_socialuser(community)
    if not bot_social_user:
        return
    qs = UserCategoryRelationship.objects.filter(
        category__in=categories,
        community=community,
        social_user__social_media=twitter,
    ).exclude(
        category__in=Category.objects.filter(
            community_relationship__do_not_follow=True,
            community_relationship__community=community,
        )
    )
    for category in categories:
        for trust in Trust.objects.filter(
            from_community=community,
            category=category,
            authorized=True
        ):
            qs |= UserCategoryRelationship.objects.filter(
                category=category,
                community=trust.to_community,
                social_user__social_media=twitter,
            ).exclude(
                category__in=Category.objects.filter(
                    community_relationship__do_not_follow=True,
                    community_relationship__community=community,
                )
            )
    if exclude_pending_follow_request:
        qs = qs.exclude(social_user__twitter_follow_request=bot_social_user)
    member_id: List[int] = (
        qs.distinct().values_list("social_user__user_id", flat=True)
    )
    return member_id


def get_community_member_friend(community) -> Counter:
    cnt = cache.get(f'{community.name}_member_friend')
    if not cnt:
        try:
            timeout = community.members_friends_cache.total_seconds()
        except:
            timeout = 0
        cnt = Counter()
        members_su_id = get_community_member_id(
            community,
            exclude_pending_follow_request=False
        )
        for su_id in members_su_id:
            try:
                userids = (
                    Friend.objects.filter(user__user_id=su_id)
                    .latest('id')
                    .id_list
                )
            except Friend.DoesNotExist:
                continue
            for userid in userids:
                cnt[userid]+=1 
        cache.set(f'{community.name}_member_friend', cnt, timeout)
    return cnt