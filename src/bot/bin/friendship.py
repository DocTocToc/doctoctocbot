import logging
import time
from typing import List
from community.models import Community
from bot.tweepy_api import get_api
from moderation.models import UserCategoryRelationship, SocialMedia, SocialUser
from moderation.social import update_social_ids
from community.helpers import (
    get_community_bot_socialuser,
    get_community_member_id,
    get_community_twitter_tweepy_api,
)
from constance import config
from tweepy.error import TweepError

logger = logging.getLogger(__name__)


def update_follow_request(friend_id: List[int], requestor: SocialUser):
    """Update twitter_follow_request m2m field if request was accepted
    Select all SocialUser instances that are friends of requestor with a
    twitter_follow_request for this requestor and remove it
    """
    for su in SocialUser.objects.filter(
        twitter_follow_request=requestor,
        user_id__in=friend_id
    ):
        su.twitter_follow_request.remove(requestor)

def record_follow_request(friend: int, requestor: SocialUser):
    try:
        friend_su = SocialUser.objects.get(user_id=friend)
    except SocialUser.DoesNotExist:
        return
    friend_su.twitter_follow_request.add(requestor)
    
def manage_block(friend: int, requestor: SocialUser, add: bool):
    if add is None:
        return
    try:
        friend_su = SocialUser.objects.get(user_id=friend)
    except SocialUser.DoesNotExist:
        return
    if add:
        friend_su.twitter_block.add(requestor)
    else:
        friend_su.twitter_block.remove(requestor)

def manage_active(friend, active):
    if active is None:
        return
    try:
        friend_su = SocialUser.objects.get(user_id=friend)
    except SocialUser.DoesNotExist:
        return
    friend_su.active=active
    friend_su.save()

def create_friendship_members(community: Community, users=400):
    SLEEP = config.bot__bin__friendship__create_friendship_members__sleep
    if not community or not isinstance(community, Community):
        return
    member_id: Optional[List[int]] = get_community_member_id(community)
    if not member_id:
        return
    bot_screen_name = community.account.username
    if not bot_screen_name:
        return
    bot_social_user = get_community_bot_socialuser(community)
    if not bot_social_user:
        return
    friend_id: List[int] = update_social_ids(
        user=bot_social_user,
        cached=True,
        bot_screen_name=bot_screen_name,
        relationship="friends"
    )
    if not friend_id:
        return
    update_follow_request(friend_id, requestor=bot_social_user)
    to_add_id: List[int] = list(set(member_id)-set(friend_id))
    api = get_api(username=bot_screen_name, backend=True)
    success_screen_name = []
    success_count = 0
    failure_screen_name = []
    failure_count = 0
    for user_id in to_add_id[:users]:
        try:
            sn = SocialUser.objects.get(user_id=user_id).screen_name_tag()
        except SocialUser.DoesNotExist:
            sn = ""
        try:
            res = api.create_friendship(user_id=user_id)
            logger.debug(f"{res=}")
            success_count += 1
            success_screen_name.append(sn)
            # remove eventual block status
            manage_block(
                friend=user_id,
                requestor=bot_social_user,
                add=False
            )
            manage_active(
                friend=user_id,
                active=True                  
            )
        except TweepError as e:
            logger.error(
                "Error during friendship creation for "
                f"user {user_id} / {sn} : {e}"
            )
            failure_count += 1
            failure_screen_name.append(sn)
            error_code = e.args[0][0]['code']
            #'Cannot find specified user.'
            if error_code == 108:
                manage_active(
                    friend=user_id,
                    active=False                   
                )
            elif error_code == 160:
                record_follow_request(
                    friend=user_id,
                    requestor=bot_social_user
                )
            elif error_code == 161:
                break
            elif error_code == 162:
                # mark SocialUser has having blocked bot_social_user
                manage_block(
                    friend=user_id,
                    requestor=bot_social_user,
                    add=True
                )
            continue
        logger.debug(f"{user_id=} API reply: {res}")
        # pause in seconds
        if SLEEP:
            time.sleep(SLEEP)
    logger.debug(
        f"{success_count} users added to friends: {success_screen_name=} \n"
        f"{failure_count} error(s): {failure_screen_name=}"
    )
"""
[{'code': 160, 'message': "You've already requested to follow XXX."}]
[{'code': 108, 'message': 'Cannot find specified user.'}]
[{'code': 161, 'message': "You are unable to follow more people at this time. Learn more <a href='http://support.twitter.com/articles/66885-i-can-t-follow-people-follow-limits'>here</a>."}]
[{'code': 162, 'message': 'You have been blocked from following this account at the request of the user.'}]
"""    
    
def create_friendship(userid, community: Community):
    if not community or not isinstance(community, Community):
        return
    api = get_community_twitter_tweepy_api(community, backend=True)
    if not api:
        return
    try:
        api.create_friendship(user_id=userid)
    except TweepError as e:
        logger.error(f"Tweepy Error: {e}")
        return
    except AttributeError as e:
        logger.error(f"Attribute Error: {e}")
        return