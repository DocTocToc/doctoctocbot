import logging
import ast
import random
import os
from datetime import datetime, timedelta
import pytz
from typing import List
from django.utils import timezone
from django.db import (
    IntegrityError,
    DatabaseError,
)
from django.db.models import F
from django.conf import settings
from django.utils.translation import activate
from community.models import Trust
from common.twitter import status_url_from_id
from moderation.models import (
    Queue,
    Moderation,
    CategoryMetadata,
    Moderator,
    UserCategoryRelationship,
    SocialUser,
)
from moderation.social import update_social_ids
from moderation.dm import sendmoderationdm
from community.models import Retweet
from community.models import Community
from dm.api import senddm_tweepy
from optin.models import Option, OptIn
from constance import config
from moderation.profile import screen_name
from common.twitter import get_url_from_user_id
from django.utils.translation import gettext as _
from humanize.time import precisedelta

logger = logging.getLogger(__name__)

def process_unknown_user(user_id, status_id, hrh):
    logger.debug("processing unknown user")
    logger.debug(f"hrh.hashtag_mi_lst: {hrh.hashtag_mi_lst}")
    dct_lst = Retweet.objects.filter(retweet=True) \
                                .filter(hashtag__in=hrh.hashtag_mi_lst) \
                                .values(
                                    community_name=F('community__name'),
                                    username=F('community__account__username')
                                ) \
                                .order_by('community').distinct('community')
    logger.debug(f"dct_lst: {dct_lst}")
    for dct in dct_lst:
        logger.debug(f'{dct=}')
        addtoqueue(
            user_id,
            status_id,
            dct['community_name']
        )

def warn_senior_moderator(user_id, status_id, community):
    info=_(
        "Current moderations for user {user_id} with {community} exist."
    ).format(user_id=user_id, community=community)
    if status_id:
        info+=_(
            "\nUser added a status update: {status_url}"
        ).format(status_url=status_url_from_id(status_id))
    logger.info(info)
    sn = screen_name(user_id)
    if sn:
        user_tag =f"@{sn}"
    else:
        user_tag = get_url_from_user_id(user_id)
    dm_txt = _("User {user_tag} is waiting for moderation\n") \
        .format(user_tag=user_tag)
    dm_txt+=info
    senior_moderator = Moderator.objects \
        .filter(community=community, senior=True, active=True).first()
    logger.debug(f"{senior_moderator=}")
    if not senior_moderator:
        return
    res = senddm_tweepy(
        dm_txt,
        senior_moderator.socialuser.user_id,
        screen_name=community.account.username
    )
    logger.debug(f"{res=}")

def addtoqueue(user_id, status_id, community_name):
    try:
        community = Community.objects.get(name=community_name)
    except Community.DoesNotExist as e:
        logger.error(e)
        return
    # Is there already a Moderation for this user and this community?
    mod_qs = Moderation.objects.current.filter(
        queue__user_id = user_id,
        queue__community = community,
    )
    logger.debug(f'{mod_qs=}')
    if mod_qs.exists():
        logger.debug(f"Moderation already exists: {mod_qs=}")
        warn_senior_moderator(user_id, status_id, community)
        return
    try:
        queue, created = Queue.objects.get_or_create(
            user_id = user_id,
            status_id = status_id,
            community = community
        )
        logger.debug(f'{queue}')
        if created:
            create_initial_moderation(queue)
    except IntegrityError:
        logger.error(
            "Integrity error while attempting to get_or_create Queue with "
            f"{user_id=} {status_id=} {community=}"
        )
    except Queue.MultipleObjectsReturned:
        logger.error(
            "MultipleObjectsReturned error while attempting to"
            "get_or_create Queue with "
            f"{user_id=} {status_id=} {community=}"
        )
    except Exception as e:
        raise e

def remove_done_moderations(community_name):
    try:
        community = Community.objects.get(name=community_name)
    except Community.DoesNotExist as e:
        logger.error(e)
        return
    moderation_qs = Moderation.objects.current.filter(
        queue__community__id=community.id,
        state__isnull=True,
    )
    counter = 0
    for moderation in moderation_qs:
        ucr_qs = UserCategoryRelationship.objects.filter(
            social_user__user_id = moderation.queue.user_id,
            community = community,
        )
        for ucr in ucr_qs:
            # if there is a ucr that is not a self moderation
            if ucr.moderator.user_id != ucr.social_user.user_id:
                moderation.queue.delete()
                counter += 1
                break
    return counter



def create_initial_moderation(queue):
    """
    MODERATOR = 'moderator'
    SENIOR = 'senior'
    DEVELOPER = 'developer'
    FOLLOWER = 'follower'
    SELF = 'self'
    """
    random.seed(os.urandom(128))
    if settings.MODERATION["dev"]:
        mod=developer_mod(queue)
    elif queue.type == Queue.MODERATOR:
        mod=moderator_mod(queue)
    elif queue.type == Queue.SENIOR:
        mod=senior_mod(queue)
    elif queue.type == Queue.DEVELOPER:
        mod=developer_mod(queue)
    elif queue.type == Queue.FOLLOWER:
        mod=follower_mod(queue)
    elif queue.type == Queue.SELF:
        mod=self_mod(queue)
    logger.debug(f"{mod=}")
    sendmoderationdm(mod)

def developer_mod(queue):
    uid: List = SocialUser.objects.devs()
    logger.debug(f"SocialUser.objects.devs(): {uid}")
    if not uid:
        return senior_mod(queue)
    else:
        chosen_mod_uid = random.choice(uid)
        return create_moderation_instance(chosen_mod_uid, queue)

def senior_mod(queue):
    uid: List = SocialUser.objects.active_moderators(
        queue.community,
        senior=True
    )
    logger.debug(
        f"SocialUser.objects.active_moderators(queue.community, senior=True): "
        f"{uid}"
    )
    if not uid:
        return moderator_mod(queue)
    else:
        chosen_mod_uid = random.choice(uid)
        return create_moderation_instance(chosen_mod_uid, queue)

def moderator_mod(queue):
    uid: List = SocialUser.objects.active_moderators(
        queue.community,
    )
    logger.debug(
        f"SocialUser.objects.active_moderators(queue.community, senior=False):"
        f"{uid}"
    )
    if not uid:
        return
    chosen_mod_uid = random.choice(uid)
    logger.debug(f"{chosen_mod_uid=}")
    return create_moderation_instance(chosen_mod_uid, queue)

def follower_mod(queue):
    def choose_follower(uid):
        if not uid:
            return
        chosen_mod_uid = random.choice(uid)
        try:
            socialuser = SocialUser.objects.get(user_id=uid)
        except SocialUser.DoesNotExist:
            return chosen_mod_uid
        try:
            option = Option.objects.get(name='twitter_dm_moderation_follower')
        except Option.DoesNotExist:
            return chosen_mod_uid
        try:
            optin = OptIn.objects.get(
                option=option,
                socialuser=socialuser
            )
        except OptIn.DoesNotExist:
            return chosen_mod_uid
        if not optin.authorize:
            uid.remove(chosen_mod_uid)
            return choose_follower(uid)
    try:
        su = SocialUser.objects.get(user_id=queue.user_id)
    except SocialUser.DoesNotExist:
        return
    uid = verified_follower(su, queue.community)
    logger.debug(f"{uid}")
    if not uid:
        senior_mod(queue)
    else:
        chosen_mod_uid = choose_follower(uid)
        if not chosen_mod_uid:
            senior_mod(queue)
            return
        return create_moderation_instance(chosen_mod_uid, queue)

def self_mod(queue):
    ok = False
    try:
        su = SocialUser.objects.get(user_id = queue.user_id)
    except SocialUser.DoesNotExist:
        return
    try:
        option = Option.objects.get(name='twitter_dm_moderation_self')
    except Option.DoesNotExist:
        return
    try:
        optin = OptIn.objects.as_of().get(
            option=option,
            socialuser=su
        )
        ok=optin.authorize
    except OptIn.DoesNotExist:
        ok=True
    logger.debug(f'{ok=}')
    if ok:
        return create_moderation_instance(queue.user_id, queue)

def create_moderation_instance(userid: int, queue: Queue):
    try:
        moderator_mi = SocialUser.objects.get(user_id=userid)
    except SocialUser.DoesNotExist:
        return
    community = queue.community
    if queue.type == Queue.SELF:
        interval = community.pending_self_moderation_period
    else:
        interval = community.moderator_moderation_period
    try:
        moderation = Moderation.objects.filter(
            moderator=moderator_mi,
            queue=queue
        ).latest('version_start_date')
    except Moderation.DoesNotExist:
        moderation = None
    if moderation and interval:
        if (timezone.now() - moderation.version_start_date) < interval:
            logger.warn(
                f'Moderation for same queue / moderator created less than '
                f'{precisedelta(interval)} ago.'
            )
            return
    try:
        return Moderation.objects.create(
            moderator=moderator_mi,
            queue=queue
        )
    except DatabaseError as e:
        logger.error(f"Error during creation of initial moderation:\n{e}")

def verified_follower(su: SocialUser, community) -> List[int]:
    try:
        bot_screen_name = community.account.username
    except:
        bot_screen_name = None 
    followers = update_social_ids(
        su,
        bot_screen_name=bot_screen_name,
        relationship='followers',
    )
    if not followers:
        return
    # who do we trust?
    ucr_qs = UserCategoryRelationship.objects.none()
    logger.debug(f"{ucr_qs}")
    for trust in Trust.objects.filter(from_community=community):
        ucr_qs |= UserCategoryRelationship.objects.filter(
            category = trust.category,
            community = trust.to_community,
        )
        logger.debug(f"{ucr_qs}")
    # exclude self moderations
    ucr_qs = ucr_qs.exclude(social_user=F('moderator'))
    logger.debug(f"{ucr_qs}")
    if not ucr_qs:
        return
    return SocialUser.objects.filter(
        user_id__in=followers,
        id__in=ucr_qs.values_list('social_user', flat=True)
    ).values_list('user_id', flat=True)
    
def self_categorize(socialuser: SocialUser, community: Community):
    def is_backoff(start: datetime, backoff_delta: timedelta):
        if not backoff_delta:
            return False
        return (datetime.now(pytz.utc) - start) < backoff_delta
    # days
    backoff = config.moderation__self_categorize__backoff
    backoff_delta = timedelta(days=backoff)
    try:
        queue = Queue.objects.filter(
            user_id=socialuser.user_id,
            community=community,
            type=Queue.SELF
        ).latest('version_start_date')
    except Queue.DoesNotExist:
        queue =None
    if not queue or not is_backoff(queue.version_start_date, backoff_delta):
        try:
            queue = Queue.objects.create(
                user_id=socialuser.user_id,
                community=community,
                type=Queue.SELF
            )
        except DatabaseError as e:
            logger.error(e)
            return
        create_initial_moderation(queue)
