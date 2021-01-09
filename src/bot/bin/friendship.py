import logging
from typing import List
from community.models import Community
from bot.tweepy_api import get_api
from moderation.models import UserCategoryRelationship, SocialMedia, SocialUser
from moderation.social import update_social_ids
from community.helpers import get_community_bot_socialuser

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

def create_friendship_members(community: Community, users=400):
    if not community or not isinstance(community, Community):
        return
    categories = community.membership.all()
    try:
        twitter = SocialMedia.objects.get(name="twitter")
    except SocialMedia.DoesNotExist:
        return
    bot_social_user = get_community_bot_socialuser(community)
    if not bot_social_user:
        return
    member_id: List[int] = (
        UserCategoryRelationship.objects
        .filter(
            category__in=categories,
            community=community,
            social_user__social_media=twitter,
        )
        .exclude(social_user__twitter_follow_request=bot_social_user)
        .values_list("social_user__user_id", flat=True)
    )
    if not member_id:
        return
    bot_screen_name = community.account.username
    if not bot_screen_name:
        return
    friend_id: List[int] = update_social_ids(
        user=bot_social_user,
        cached=False,
        bot_screen_name=bot_screen_name,
        relationship="friends"
    )
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
            success_count += 1
            success_screen_name.append(sn)
        except TweepError as e:
            logger.error(
                "Error during friendship creation for "
                f"user {user_id} / {sn} : {e}"
            )
            failure_count += 1
            failure_screen_name.append(sn)
            if e.args[0][0]['code'] == 160:
                record_follow_request(
                    friend=user_id,
                    requestor=bot_social_user
                )
            continue
        logger.debug(f"{user_id=} API reply: {res}")
    logger.debug(
        f"{success_count} users added to friends: {success_screen_name=} \n"
        f"{failure_count} error(s): {failure_screen_name=}"
    )
"""
[{'code': 160, 'message': "You've already requested to follow XXX."}]
[{'code': 108, 'message': 'Cannot find specified user.'}]
"""    
    
    