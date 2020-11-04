from social_django.models import UserSocialAuth
from moderation.models import SocialUser, SocialMedia
from community.models import AccessLevel, Retweet
from constance import config
from typing import List
from moderation.models import Category
from bot.doctoctocbot import is_follower
import logging

logger = logging.getLogger(__name__)


def get_all_categories(user, community):
    su = get_twitter_social_user(user)
    # determine the categories the user belongs to
    return get_all_categories_from_social_user(su, community)

def get_all_categories_from_social_user(su, community):
    # determine the categories the user belongs to
    category: List[Category] = []
    # check twitter
    try:
        category.extend(twitter_categories_from_social_user(su, community))
    except TypeError:
        pass
    # check local social network
    try:
        category.extend(local_categories_from_social_user(su, community))
    except TypeError:
        pass
    # remove duplicates
    return list(set(category))

def member_level(user, community, category):
    if any(cat in category for cat in community.membership.all()):
        return access_level_object("member")

def broadcast_level(user, community, category):
    broadcast_categories = [rt.category for rt in Retweet.objects.filter(
        community=community,
        retweet=True
        )]
    if any(cat in category for cat in broadcast_categories):
        return access_level_object("broadcast")

def follower_level(user, community, category):
    follower_categories = community.follower.all()
    # local
    su_local = get_local_social_user(user)
    if su_local:
        if any(cat in category for cat in follower_categories):
            return access_level_object("follower")
    # twitter
    su_twitter = get_twitter_social_user(user)
    if su_twitter:
        protected = community.account.protected
        is_follower = is_follower(
            su_twitter.user_id,
            community.account.username
        )
        allowed = any(cat in category for cat in follower_categories)
        if protected:
            if allowed and is_follower:
                return access_level_object("follower")
            else:
                return
        elif is_follower:
            return access_level_object("follower")

def get_api_level(user, community):
    if not user.is_authenticated:
        return access_level_object("anonymous")
    category: List[Category] = get_all_categories(user, community)
    member = member_level(user, community, category)
    if member:
        return member
    broadcast = broadcast_level(user, community, category)
    if broadcast:
        return broadcast
    follower = follower_level(user, community, category)
    if follower:
        return follower
    return access_level_object("registered")

def access_level_object(level):
    try:
        return AccessLevel.objects.get(name=level)
    except AccessLevel.DoesNotExist:
        logger.error(f"{level} access level was not created")
        return None

def twitter_categories(user, community):
    su = get_twitter_social_user(user)
    if su:
        return twitter_categories_from_social_user(su, community)

def twitter_categories_from_social_user(su, community):
    category: List(Category) = []
    if su and community:
        category.extend(
            category_list(
                community,
                su.categoryrelationships.exclude(moderator=su).distinct()
            )
        )
    #logger.debug(f"{category=}")
    return category

def local_categories(user, community):
    su = get_local_social_user(user)
    if su:
        return local_categories_from_social_user(su, community)

def local_categories_from_social_user(su, community):
    category: List(Category) = []
    if su and community:
        category.extend(
            category_list(
                community,
                su.categoryrelationships.exclude(moderator=su).distinct()
            )
        )
    #logger.debug(f"{category=}")
    return category

def category_list(community, usercategoryrelationships):
    category: List[Category] = []
    for cr in usercategoryrelationships:
        if cr.community == community or cr.community in community.trust.all():
            category.append(cr.category)
    return category

def get_twitter_social_user(user):
    """If it exists, get Twitter SocialUser from Django user 
    """
    try:
        twitter_soc_med = SocialMedia.objects.get(name="twitter")
    except SocialMedia.DoesNotExist:
        return
    try:
        user_social_auth = UserSocialAuth.objects.get(
            user=user,
            provider="twitter",
        )
    except UserSocialAuth.DoesNotExist:
        return
    try:
        return SocialUser.objects.get(
            user_id=user_social_auth.uid,
            social_media = twitter_soc_med,
        )
    except SocialUser.DoesNotExist:
        return
    
def get_local_social_user(user):
    try:
        local_soc_med = SocialMedia.objects.get(name=config.local_social_media)
    except SocialMedia.DoesNotExist:
        return
    try:
        return SocialUser.objects.get(
            user_id=user.id,
            social_media = local_soc_med,
        )
    except SocialUser.DoesNotExist:
        return
    
