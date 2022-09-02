import time
import datetime
import random
from typing import Optional
from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.urls import reverse
from django.conf import settings
from constance import config
from webpush import send_user_notification
from versions.exceptions import DeletionOfNonCurrentVersionError

from bot.bin.user import getuser_lst
from conversation.models import Tweetdj
from moderation.profile import twitterprofile, create_update_profile
from moderation.lists.poll import poll_lists_members, create_update_lists
from moderation.moderate import (
    self_categorize,
)
from moderation.dm import create_moderation, sendmoderationdm, viral_moderation
from moderation.models import (
    Moderation,
    SocialUser,
    UserCategoryRelationship,
    CategoryMetadata,
    Moderator,
    Queue,
    Follower,
)
from request.models import Queue as Request_Queue
from common.utils import trim_grouper
from community.models import Community
from moderation.profile import check_profile_pictures
from moderation.social import update_social_ids
from celery.utils.log import get_task_logger
from moderation.poll import poll_moderation_dm
from moderation.profile import (
    update_twitter_followers_profiles,
    create_twitter_social_user_and_profile
)
from community.helpers import get_community_bot_socialuser
from bot.tweepy_api import get_api
from tweepy.error import TweepError
from moderation.moderate import self_mod, trusted_category_exists
from moderation.filter import process_onhold_queues

logger = get_task_logger(__name__)

@shared_task
def handle_poll_lists_members(community_name: str):
    poll_lists_members(community_name)

@shared_task
def handle_create_update_lists(community_name: str):
    create_update_lists(community_name)

@shared_task
def handle_create_update_profile(userid: int, bot_screen_name=None):
    create_update_profile(userid, bot_screen_name)

def handle_create_all_profiles():
    user_id_lst = SocialUser.objects.filter(
        profile__isnull=True
    ).values_list('user_id', flat=True)
    user_id_request_lst = []

    for user_id in user_id_lst:
        try:
            tweetdj_mi = Tweetdj.objects.filter(
                userid = user_id,
                json__isnull=False,
            ).latest()
        except Tweetdj.DoesNotExist:
            user_id_request_lst.append(user_id)
            continue
        logger.debug(f"type: {type(tweetdj_mi.json)} \n value:{tweetdj_mi.json}")
        try:
            userjson = tweetdj_mi.json.get("user")
        except AttributeError:
            continue
        twitterprofile(userjson)

    if user_id_request_lst:
        for user_id_lst in trim_grouper(user_id_request_lst, 100):
            user_jsn_lst = getuser_lst(user_id_lst)
            if not user_jsn_lst:
                continue
            for user_jsn in user_jsn_lst:
                twitterprofile(user_jsn)

@shared_task
def handle_check_all_profile_pictures():
    userid_lst = SocialUser.objects.values_list('user_id', flat=True)
    for userid in userid_lst:
        check_profile_pictures(userid)

@shared_task
def handle_sendmoderationdm(mod_instance_id):
    logger.debug(f'inside handle_sendmoderationdm({mod_instance_id})')
    try:
        moderation = Moderation.objects.get(pk=mod_instance_id)
    except Moderation.DoesNotExist:
        logger.error(f"Moderation with id={id} does not exist.")
        return
    sendmoderationdm(moderation)

@shared_task
def handle_poll_moderation_dm(community: str):
    poll_moderation_dm(community)

@shared_task
def handle_all_poll_moderation_dm():
    for community in Community.objects.filter(active=True):
        handle_poll_moderation_dm.apply_async(args=(community.name,))

@shared_task
def update_moderators_friends():
    for dct in Moderator.objects.filter(active=True).values(
        'socialuser',
        'community'
    ).order_by('socialuser__id').distinct('socialuser'):
        su = SocialUser.objects.get(id=dct["socialuser"])
        community = Community.objects.get(id=dct["community"])
        update_social_ids(
            su,
            cached=True,
            bot_screen_name=community.account.username,
            relationship='friends',
        )
        time.sleep(settings.API_FRIENDS_PERIOD)

@shared_task
def handle_twitter_followers(user_id, bot_screen_name):
        try:
            su = SocialUser.objects.get(user_id=user_id)
        except SocialUser.DoesNotExist:
            return
        update_social_ids(
            su,
            cached=False,
            bot_screen_name=bot_screen_name,
            relationship='followers',
        )

@shared_task
def handle_twitter_friends(user_id, bot_screen_name):
        try:
            su = SocialUser.objects.get(user_id=user_id)
        except SocialUser.DoesNotExist:
            return
        update_social_ids(
            su,
            cached=False,
            bot_screen_name=bot_screen_name,
            relationship='friends',
        )

@shared_task
def handle_pending_moderations():
    logger.debug("handle_pending_moderations()")
    for mod in Moderation.objects.current.filter(state__isnull=True):
        if not mod.is_current:
            continue
        try:
            queue = mod.queue
        except (KeyError, Queue.DoesNotExist) as e:
            logger.warn(f"No Queue for Moderation {mod} {e}")
            continue
        # don't reallocate queues with type SENIOR or DEVELOPER
        # TODO: recheck followers and send moderation to verified follower
        if queue.type in [Queue.SENIOR, Queue.DEVELOPER]:
            continue
        if queue.type == Queue.SELF:
            self_mod(queue)
            continue
        try:
            community = queue.community
            if not community:
                continue
        except KeyError:
            continue
        user_id = mod.queue.user_id
        su = SocialUser.objects.get(user_id=user_id)
        # check if ucr created by community already exists:
        if (
            UserCategoryRelationship.objects
            .filter(social_user=su, community=community)
            .exclude(moderator=su).exists()
        ):
            expire_and_delete(mod)
            continue
        # check if trusted ucr already exists
        if trusted_category_exists(su, community):
            expire_and_delete(mod)
            continue
        # TODO: add default pending moderation period in settings
        # return if not set
        delta : timedelta = community.pending_moderation_period
        if not delta:
            delta=datetime.timedelta()
        dtnow = datetime.datetime.now(tz=datetime.timezone.utc)
        dt = dtnow - delta
        if mod.version_start_date > dt:
            continue
        moderator_is_senior = Moderator.objects.filter(
            community=community,
            socialuser=mod.moderator,
            senior=True,
        ).exists()
        # give pending FOLLOWER moderation to senior moderator
        if queue.type == Queue.FOLLOWER:
            if moderator_is_senior:
                continue
            else:
                new_mod = create_moderation(
                    mod.queue.community,
                    mod.queue,
                    senior=True,
                )
                try:
                    handle_sendmoderationdm.apply_async(args=(new_mod.id,))
                    expire_and_delete(mod)
                except AttributeError as e:
                    logger.error(f'{new_mod=}: {e}')
        moderator_exclude: List[int] = list(
            Moderation.objects.filter(queue=mod.queue)
            .values_list('moderator__id', flat=True)
            .order_by('moderator__id').distinct('moderator')
        )
        logger.debug(f"moderator_exclude: {moderator_exclude}")
        new_mod = create_moderation(
            mod.queue.community,
            mod.queue,
            exclude=moderator_exclude,
            senior=False,
        )
        try:
            handle_sendmoderationdm.apply_async(args=(new_mod.id,))
            expire_and_delete(mod)
        except AttributeError as e:
            logger.error(f'{new_mod=}: {e}')

def expire_and_delete(moderation):
        try:
            state = CategoryMetadata.objects.get(name='expired')
        except CategoryMetadata.DoesNotExist:
            state = None
        moderation.state = state
        moderation.save()
        try:
            moderation.delete()
        except DeletionOfNonCurrentVersionError:
            pass

@shared_task   
def handle_viral_moderation(socialuser_id):
    viral_moderation(socialuser_id, cached=False)

@shared_task
def handle_accept_follower(ucr_pk: int):
    """handle_accept_follower
    
    Process newly categorized social user to check if they should be allowed
    in as follower by protected social media accounts.
    
    ucr: pk of UserCategoryRelationship instance
    """
    #noop
    return

    try:
        ucr = UserCategoryRelationship.objects.get(pk=ucr_pk)
        logger.debug(f"ucr: {ucr}")
    except UserCategoryRelationship.DoesNotExist:
        return
    # return if community account is not protected 
    try:
        protected = ucr.community.account.protected
        logger.debug(f"{protected =}")
    except:
        return
    if not protected:
        return
    # Is there a pending request queue for this socialuser and this community?
    for pending_request in Request_Queue.objects.current.filter(
        socialuser = ucr.social_user,
        community = ucr.community,
        state = Request_Queue.PENDING,
        ):
        if pending_request.socialmedia.name == 'twitter':
            handle_accept_follower_twitter.apply_async(
                args=[ucr.pk],
            )

"""handle_accept_follower_twitter

Process newly categorized social user to check if they should be allowed
in as follower by protected social media accounts.

ucr: pk of UserCategoryRelationship instance
"""
@shared_task
def handle_accept_follower_twitter(ucr_pk: int):
    return
    """
    try:
        ucr = UserCategoryRelationship.objects.get(pk=ucr_pk)
    except UserCategoryRelationship.DoesNotExist:
        return
    if ucr.category in ucr.community.follower.all():
        uid = ucr.social_user.user_id
        username = ucr.community.account.username
        success = False
        success = accept_follower(
            uid,
            username,
        )
        if success:
            #accept_queue
    else:
        return
        decline_follower(
            ucr.social_user.user_id,
            ucr.community.account.username,
        )
    """

@shared_task
def handle_update_twitter_followers_profiles(community: str):
    """Update Profiles for followers of the community's bot

    Parameters
    ----------
    community : str
        Name of the community
    """
    if not community:
        return
    try:
        community_mi = Community.objects.get(name=community)
    except Community.DoesNotExist:
        return
    update_twitter_followers_profiles(community_mi)

@shared_task
def handle_create_twitter_socialuser(
        screen_name: str,
        username: str,
        domain: str,
        community: Community,
    ):
    if not screen_name:
        return
    api = get_api(username=community.account.username)
    if not api:
        logger.error(
            f'Could not get functional API.'
        )
        return
    try:
        tweepy_user = get_api().get_user(screen_name=screen_name)
    except TweepError as e:
        logger.error('Tweepy error "%s' % e)
    except AttributeError as e:
        logger.error(f"AttributeError: {e}")
        return
    user_id=tweepy_user.id
    su, created = create_twitter_social_user_and_profile(user_id)
    if created and su:
        logger.debug(
            f'Done creating SocialUser object {su}.'
        )
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return
        payload = {
            "head": f"SocialUser {screen_name} created!",
            "body": f"Creation of SocialUser {screen_name} was successful.", 
            "url": f"https://{domain}{reverse('moderation:user')}?screen_name={screen_name}"
        }
        #logger.debug(payload)
        send_user_notification(
            user=user, payload=payload, ttl=1000
        )       
    elif su:
        logger.warn(
            f'SocialUser object {su} already exists.'
        )
    else:
        logger.error(
            f'Error, no new user was created.'
        )

@shared_task
def handle_self_categorize(community_id: int, max: Optional[int] = None):
    try:
        community = Community.objects.get(id=community_id)
    except Community.DoesNotExist:
        return
    bot_su = get_community_bot_socialuser(community)
    try:
        follower = Follower.objects.filter(user=bot_su).latest()
    except:
        return
    backoff = config.messenger__models__backoff_default
    for su in SocialUser.objects.filter(
        user_id__in=follower.id_list,
        category=None
    )[:max]:
        self_categorize(su, community)
        time.sleep(backoff)

@shared_task
def handle_self_moderation(community: str, count: Optional[int] = None):
    if not count:
        return
    try:
        community = Community.objects.get(name=community)
    except Community.DoesNotExist:
        return
    bot: SocialUser = community.account.socialuser
    if not bot:
        return
    try:
        follower = Follower.objects.filter(user=bot).latest()
    except Follower.DoesNotExist:
        return
    exclude_user_id = Queue.objects.current.filter(
        community=community,
        type=Queue.SELF,
    ).values_list('user_id', flat=True)
    no_cat_su = list(SocialUser.objects
        .filter(
            category=None,
            user_id__in=follower.id_list
        )
        .exclude(
            user_id__in=exclude_user_id
        )
    )
    if not no_cat_su:
        return
    k = min(len(no_cat_su), count)
    su_candidates = random.sample(no_cat_su, k)
    if not su_candidates:
        return
    for su in su_candidates:
        self_categorize(su, community)

@shared_task
def handle_onhold_queues():
    for c in Community.objects.filter(
        active=True,
        moderation_filter__isnull=False
    ):
        process_onhold_queues(c)

@shared_task
def handle_all_socialuser_language(per_page: int = 100):
    queryset = SocialUser.objects.all().filter(language__isnull=True)
    paginator = Paginator(queryset, per_page)
    for page_number in paginator.page_range:
        page = paginator.page(page_number)
        for su in page.object_list:
            logger.debug(f'{su=}')
            tli=su.get_language()
            logger.debug(f'{tli=}')
            su.language=tli
            su.save()
            logger.debug(f'{su.language=}')

@shared_task
def handle_socialuser_language(pk):
    try:
        su = SocialUser.objects.get(pk=pk)
    except SocialUser.DoesNotExist:
        return
    su.language=su.get_language()
    su.save()