import logging
import random
import time

from community.models import Community
from bot.bin.friendship import create_friendship_members
from community.helpers import get_community_bot_socialuser
from moderation.models import Follower, Friend
from moderation.profile import create_twitter_social_user
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def handle_follow_member():
    communities = Community.objects.filter(
        active=True,
        twitter_follow_member=True
    )
    for community in communities:
        handle_follow_member_community.apply_async(
            args=(community.name,),
            ignore_result=True
        )

@shared_task
def handle_follow_member_community(community: str):
    try:
        community = Community.objects.get(name=community)
    except Community.DoesNotExist:
        return
    create_friendship_members(community)
    
@shared_task
def handle_add_followers_to_socialusers():
    for community in Community.objects.filter(active=True):
        bot_su = get_community_bot_socialuser(community)
        if not bot_su:
            continue
        bot_follower_id = Follower.objects.filter(user=bot_su).latest().id_list
        for userid in bot_follower_id:
            create_twitter_social_user(userid)

@shared_task
def handle_add_friends_to_socialusers():
    for community in Community.objects.filter(active=True):
        bot_su = get_community_bot_socialuser(community)
        if not bot_su:
            continue
        bot_friend_id = Friend.objects.filter(user=bot_su).latest().id_list
        for userid in bot_friend_id:
            create_twitter_social_user(userid)