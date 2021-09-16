import os
import random
import time
import datetime
from typing import Optional
from versions.exceptions import DeletionOfNonCurrentVersionError
from conversation.models import Tweetdj
from celery import shared_task
from bot.bin.user import getuser_lst
from moderation.profile import twitterprofile
from moderation.lists.poll import poll_lists_members, create_update_lists
from django.conf import settings
from constance import config
from conversation.utils import screen_name
from moderation.moderate import  handle_twitter_dm_response
from django.contrib.auth import get_user_model 
from django.utils.translation import activate
from django.db import transaction, DatabaseError
from dm.models import DirectMessage
from webpush import send_user_notification
from moderation.moderate import self_categorize
from django.urls import reverse

from moderation.models import (
    Moderation,
    SocialUser,
    Category,
    UserCategoryRelationship,
    CategoryMetadata,
    Moderator,
    Queue,
    ModerationOptIn,
    Follower,
)
from request.models import Queue as Request_Queue
from bot.models import Account

from common.utils import trim_grouper
from django.utils.translation import gettext as _
from moderation.social import send_graph_dm
from bot.onstatus import triage_status

from moderation.moderate import quickreply
from dm.api import senddm
from community.models import Community
from moderation.profile import check_profile_pictures
from moderation.profile import (
    create_update_profile_twitter,
    create_update_profile_local,
    )
from community.helpers import activate_language
from moderation.social import update_social_ids
from celery.utils.log import get_task_logger
from moderation.moderate import viral_moderation
from moderation.profile import update_twitter_followers_profiles
from community.helpers import (
    get_community_bot_screen_name,
    get_community_bot_socialuser
)
from bot.tweepy_api import get_api
from moderation.profile import create_twitter_social_user_and_profile
from tweepy.error import TweepError
from optin.models import Option, OptIn

logger = get_task_logger(__name__)


@shared_task
def handle_poll_lists_members(community_name: str):
    poll_lists_members(community_name)
    

@shared_task
def handle_create_update_lists(community_name: str):
    create_update_lists(community_name)

@shared_task
def handle_create_update_profile(userid: int, bot_screen_name=None):
    try:
        su: SocialUser = SocialUser.objects.get(user_id=userid)
    except SocialUser.DoesNotExist:
        return
    try:
        sm: SocialMedia = su.social_media
    except AttributeError:
        return
    if sm.name == 'twitter':
        create_update_profile_twitter(
            su,
            bot_screen_name=bot_screen_name
        )
    elif sm.name == settings.THIS_SOCIAL_MEDIA:
        create_update_profile_local(su)

def handle_create_all_profiles():
    su_qs_lst = SocialUser.objects.values('user_id', 'profile')
    user_id_request_lst = []
    
    for su in su_qs_lst:
        if not su["profile"]:
            try:
                tweetdj_mi = Tweetdj.objects.filter(
                    userid = su["user_id"],
                    json__isnull=False,
                ).latest()
            except Tweetdj.DoesNotExist:
                user_id_request_lst.append(su["user_id"])
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

@shared_task(bind=True, max_retries=2)
def handle_sendmoderationdm(self, mod_instance_id):
    logger.debug(f'inside handle_sendmoderationdm({mod_instance_id})')
    # community
    try:
        mod_mi = Moderation.objects.get(pk=mod_instance_id)
    except Moderation.DoesNotExist:
        logger.error(f"Moderation with id={id} does not exist.")
        return
    bot_screen_name = get_community_bot_screen_name(
        mod_mi.queue.community
    )
    handle_create_update_profile(
        mod_mi.queue.user_id,
        bot_screen_name = bot_screen_name
    )
    # select language
    try:
        community = mod_mi.queue.community
    except:
        logger.error(f'Queue {mod_mi.queue} community field is null')
        return
    activate_language(community)

    qr = quickreply(mod_instance_id)
    logger.debug(f"qr:{qr}")
    logger.info(f"mod_mi.moderator.user_id: {mod_mi.moderator.user_id}")
    #logger.debug(f"moderator profile: {mod_mi.moderator.profile}")
    logger.info(f"mod_mi.queue.user_id {mod_mi.queue.user_id}")

    status_id = mod_mi.queue.status_id
    if status_id:
        sn = screen_name(mod_mi.queue.status_id)
        status_str = (
            _("\n Tweet: https://twitter.com/{screen_name}/status/{status_id}")
            .format(
                screen_name=sn,
                status_id=status_id,
            )
        )
    else:
        try:
            su = SocialUser.objects.get(user_id=mod_mi.queue.user_id)
            sn = su.screen_name_tag()
        except SocialUser.DoesNotExist:
            return
        status_str = ""
    if not sn:
        return
    if mod_mi.queue.type == Queue.SELF:
        self_mod_msg = community.twitter_self_moderation_dm
        if not self_mod_msg:
            logger.error(
                f'Fill out twitter_self_moderation_dm field for {community=}'
            )
            return
        dm_txt = self_mod_msg.format(screen_name=sn)
    else:
        dm_txt = (
            _(
                "Please help us verify this user: @{screen_name} \n"
                "According to your knowledge or your review of the account, "
                "in which category would you put this user: @{screen_name} ?\n"
                "Please choose the most appropriate category by pushing one of the"
                " buttons below. "
                "{status_str}"
            ).format(screen_name=sn, status_str=status_str)
        )
    logger.debug(f"dm_txt: {dm_txt}")
    
    # social graph DM
    if not mod_mi.queue.type == Queue.SELF:
        res = send_graph_dm(
            mod_mi.queue.user_id,
            mod_mi.moderator.user_id,
            mod_mi.queue.community.account.username,
            _("You will soon receive a verification request for this user."),
            mod_mi.queue.community
        )
        logger.debug(f"graph: {res}")
        handle_twitter_dm_response(
            res,
            mod_mi.moderator.id,
            mod_mi.queue.community.id
        )
    # verification DM
    res = senddm(
        dm_txt,
        user_id=mod_mi.moderator.user_id,
        screen_name=mod_mi.queue.community.account.username,
        return_json=True,
        quick_reply=qr
    )
    logger.info(f"dm:{res}")
    handle_twitter_dm_response(
        res,
        mod_mi.moderator.id,
        community.id,
    )


@shared_task
def poll_moderation_dm():

    def get_moderation_metadata(dm):
        try:
            return dm.jsn['kwargs']['message_create']['message_data']['quick_reply_response']['metadata']
        except:
            return dm.jsn['quick_reply_response']['metadata']

    def get_moderation_id(dm):
        return get_moderation_metadata(dm)[10:46]
    
    def get_moderation_category_name(dm):
        return get_moderation_metadata(dm)[46:]
    
    current_mod_uuids = [
        str(mod.id) for mod in Moderation.objects.current.filter(state=None)
    ]
    logger.debug(f"current_mod_uuids: {current_mod_uuids}")
    # return if no current Moderation object
    if not current_mod_uuids:
        return
    bot_id_lst = Community.objects.values_list("account__userid", flat=True)
    #logger.info(f"current_moderations_uuid_str_lst: {current_moderations_uuid_str_lst}")
    """
    try:
        dms_old = (
            DirectMessage.objects
            .filter(recipient_id__in=bot_id_lst)
            .filter(jsn__kwargs__message_create__message_data__quick_reply_response__metadata__startswith="moderation")
        )
    except:
        pass
    """
    try:
        dms = (
            DirectMessage.objects
            .filter(recipient_id__in=bot_id_lst)
            .filter(jsn__quick_reply_response__metadata__startswith="moderation")
        )
    except:
        logger.error("Could not get the moderation DMs.")
        return
    logger.info(f"all moderation direct messages answers: {len(dms)} {[dm.text + os.linesep for dm in dms]}")
    if not dms:
        return
    dms_current = []
    for dm in dms:
        uid = get_moderation_id(dm)
        ok = uid in current_mod_uuids
        if ok:
            dms_current.append(dm)
    
    #logger.info(f"current moderation direct messages answers: {len(dms_current)} {[dm.text + os.linesep for dm in dms_current]}")
    for dm in dms_current:
        moderation_id = get_moderation_id(dm)
        mod_cat_name = get_moderation_category_name(dm)
        #logger.debug(f"dm moderation_id: {moderation_id}, cat: {mod_cat_name}")
        #retrieve moderation instance
        try:
            mod_mi = Moderation.objects.get(id=moderation_id)
        except Moderation.DoesNotExist as e:
            logger.error(f"Moderation object with id {moderation_id} "
                         f"does not exist. Error message: {e}")
            continue
        #logger.debug(f"mod_mi:{mod_mi}")
        # if mod_mi is not the current version, current_version() returns None
        # and it means this moderation was already done and we pass
        is_current = bool(Moderation.objects.current_version(mod_mi))
        if not is_current:    
            logger.info(f"Moderation instance {mod_mi} was already moderated.")
            continue
        
        # determine id of moderated user
        su_id_int = mod_mi.queue.user_id
        
        # moderated SocialUser instance
        try:
            moderated_su_mi = SocialUser.objects.get(user_id=su_id_int)
        except SocialUser.DoesNotExist:
            continue
        
        # Category (cat_mi) or CategoryMetadata (meta_mi) model instance
        try:
            cat_mi = Category.objects.get(name=mod_cat_name)
        except Category.DoesNotExist:
            cat_mi = None
            try:
                meta_mi = CategoryMetadata.objects.get(name=mod_cat_name)
            except CategoryMetadata.DoesNotExist:
                continue
        # moderator SocialUser instance
        try:
            moderator_su_mi = SocialUser.objects.get(user_id=dm.sender_id)
        except SocialUser.DoesNotExist:
            continue
        if cat_mi:
            process_cat_mi(cat_mi, moderated_su_mi, moderator_su_mi, mod_mi)
        elif meta_mi:
            process_meta_mi(meta_mi, moderated_su_mi, moderator_su_mi, mod_mi)

def delete_moderation_queue(mod_mi):
    with transaction.atomic():
        try:
            mod_mi.queue.delete()
        except DeletionOfNonCurrentVersionError as e:
            logger.info(f"Queue {mod_mi.queue} was already deleted. %s" % e)
        try:
            mod_mi.delete()
        except DeletionOfNonCurrentVersionError as e:
            logger.info(f"Moderation instance {mod_mi} was already moderated. %s" % e)

def process_cat_mi(cat_mi, moderated_su_mi, moderator_su_mi, mod_mi):        
    #Check if relationship already exists for the given community
    #if cat_mi in moderated_su_mi.category.all():
    community = mod_mi.queue.community
    if (moderated_su_mi.categoryrelationships
        .filter(community=community,category=cat_mi)
        .exclude(moderator=moderated_su_mi)
        .exists()):
        logger.info(f"{moderated_su_mi} is already a {cat_mi} for community {mod_mi.queue.community}")
        with transaction.atomic():
            mod_mi.state = get_category_metadata_done()
            mod_mi.save()
        delete_moderation_queue(mod_mi)
        return
    # TODO: check if there exists a categoryrelationship created by another
    # community where cat_mi differs and warn both communities of the discrepancy
 
    # create UserCategoryRelationship
    ucr = None
    with transaction.atomic():
        try:
            ucr = UserCategoryRelationship.objects.create(
              social_user = moderated_su_mi,
              category = cat_mi,
              moderator = moderator_su_mi,
              community = community
            )
        except DatabaseError as e:
            logger.error(e)
            return
    if ucr:
        logger.info(f"ucr creation successful: {ucr}")
        mod_mi.state = get_category_metadata_done()
        mod_mi.save()
        status_id = mod_mi.queue.status_id
        # delete queue object corresponding to this moderation
        # linked moderations will be deleted too
        delete_moderation_queue(mod_mi)
        # send status to triage, it will be retweeted according to retweet rules of communities
        triage_status(status_id, community)
        # TODO: create a cursor based on DM timestamp to avoid processing all DMs during each polling
        # TODO: check that the moderator is following the bot before attempting to send a DM
        # viral:
        if community.viral_moderation:
            handle_viral_moderation.apply_async(args=(moderated_su_mi.id,))

def process_meta_mi_stop(
        meta_mi,
        moderated_su_mi,
        moderator_su_mi,
        mod_mi,
        type
    ):
    if type not in [Queue.SELF, Queue.FOLLOWER]:
        return
    try:
        option = Option.objects.get(name=f'twitter_dm_moderation_{type}')
    except Option.DoesNotExist:
        return        
    try:
        mod_optin = ModerationOptIn.objects.get(
            option=option,
            type=type
        )
    except ModerationOptIn.DoesNotExist:
        return
    optin = OptIn.objects.current.filter(
        option=option,
        socialuser=moderator_su_mi
    ).first()
    if optin:
        optin = optin.clone()
        optin.authorize=mod_optin.authorize
        optin.save()
    else:
        optin = OptIn.objects.create(
            option=option,
            socialuser=moderator_su_mi,
            authorize=mod_optin.authorize   
        )
    delete_moderation_queue(mod_mi)

def process_meta_mi(meta_mi, moderated_su_mi, moderator_su_mi, mod_mi):
    """Process meta moderation answers such as 'stop', 'fail' or 'busy'
    """
    queue = mod_mi.queue
    if not queue:
        return
    community=queue.community
    if not community:
        return
    if meta_mi.name == "stop":
        logger.debug(f"SocialUser {moderator_su_mi} wants to stop.")
        # clone moderation instance, change its state to 'stop', then delete it
        with transaction.atomic():
            mod_mi.state = meta_mi
            mod_mi.save()
            mod_mi.delete()
        # if self moderation, create/update optin
        if mod_mi.queue.type in [Queue.SELF, Queue.FOLLOWER]:
            process_meta_mi_stop(
                meta_mi, 
                moderated_su_mi,
                moderator_su_mi,
                mod_mi,
                queue.type
            )
            return
        if mod_mi.queue.type == Queue.MODERATOR:
            # make moderator inactive
            moderator_mi = moderator_su_mi.moderator.filter(
                active=True,
                community=community
            ).first()
            if moderator_mi:
                moderator_mi.public=False
                moderator_mi.active=False
                moderator_mi.save()
                # create new moderation
                create_moderation(
                    community,
                    queue,
                )
        # if STOP answer comes from dev or senior, consider it as mistake
        if mod_mi.queue.type in [Queue.DEVELOPER, Queue.SENIOR]:
            pass
    elif meta_mi.name == "fail":
        logger.debug(f"SocialUser {moderator_su_mi}: fail")
        # clone moderation instance and change its state to 'fail'
        with transaction.atomic():
            mod_mi.state = meta_mi
            mod_mi.save()
            mod_mi.delete()
        # create new moderation with senior moderator
        create_moderation(
            community,
            queue,
            senior=True,
        )
    elif meta_mi.name == "busy":
        logger.debug(f"SocialUser {moderator_su_mi} is busy.")
        # clone moderation instance and change its state to 'busy'
        with transaction.atomic():
            mod_mi.state = meta_mi
            mod_mi.save()
            mod_mi.delete()
        # create new moderation excluding this busy social_user
        create_moderation(
            community,
            queue,
            exclude=moderator_su_mi,
            senior=False,
        )

def create_moderation(community, queue, exclude=None, senior=False):
    qs = Moderator.objects.filter(
        community=community,
        active=True,
    )
    if senior:
        qs = qs.filter(senior=True)
    logger.debug(f"create_moderation QuerySet (before excluding {exclude}): {qs}")
    if isinstance(exclude, SocialUser):
        qs=qs.exclude(socialuser=exclude)
    elif isinstance(exclude, list):
        qs=qs.exclude(socialuser__id__in=exclude)
    if not qs:
        qs = Moderator.objects.filter(
            community=community,
            active=True,
            senior=True,
        )
    if not qs:
        return
    logger.debug(f"create_moderation QuerySet (after excluding {exclude}): {qs}")
    random.seed(os.urandom(128))
    new_moderator_mi = random.choice(qs)
    logger.debug(f"new_moderator_mi: {new_moderator_mi}")
    try:
        new_mod_mi = Moderation.objects.create(
            moderator = new_moderator_mi.socialuser,
            queue = queue,
        )
        logger.debug(f"new_mod_mi: {new_mod_mi}")
    except:
        return
    
def get_category_metadata_done():
    try:
        return CategoryMetadata.objects.get(name='done')
    except CategoryMetadata.DoesNotExist:
        return None

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
def update_bots_followers():
    for account in Account.objects.filter(active=True):
        try:
            su = SocialUser.objects.get(user_id=account.userid)
        except SocialUser.DoesNotExist:
            continue
        update_social_ids(
            su,
            cached=True,
            bot_screen_name=account.username,
            relationship='followers',
        )
        try:
            period = settings.API_FOLLOWERS_PERIOD
            time.sleep(period)
        except AttributeError:
            logger.error(f"API_FOLLOWERS_PERIOD is not set.")
            pass

@shared_task
def update_bots_friends():
    for account in Account.objects.filter(active=True):
        try:
            su = SocialUser.objects.get(user_id=account.userid)
        except SocialUser.DoesNotExist:
            continue
        update_social_ids(
            su,
            cached=True,
            bot_screen_name=account.username,
            relationship='friends',
        )
        try:
            period = settings.API_FRIENDS_PERIOD
            time.sleep(period)
        except AttributeError:
            logger.error(f"API_FRIENDS_PERIOD is not set.")
            pass

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
        try:
            queue = mod.queue
        except (KeyError, Queue.DoesNotExist) as e:
            logger.warn(f"No Queue for Moderation {mod} {e}")
            continue
        try:
            community = queue.community
            if not community:
                continue
        except KeyError:
            continue
        # check if category already exists:
        user_id = mod.queue.user_id
        su = SocialUser.objects.get(user_id=user_id)
        if (
            UserCategoryRelationship.objects
            .filter(social_user=su, community=community)
            .exclude(moderator=su).exists()
        ):
            continue
        # TODO: add default pending moderation period in settings
        # return if not set
        period : int = community.pending_moderation_period
        if not period:
            continue
        dtnow = datetime.datetime.now(tz=datetime.timezone.utc)
        delta = datetime.timedelta(hours=period)
        dt = dtnow - delta
        if mod.version_start_date > dt:
            continue
        # don't reallocate queues with type SENIOR or DEVELOPER
        # TODO: recheck followers and send moderation to verified follower
        if queue.type in [Queue.SENIOR, Queue.DEVELOPER]:
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
                create_moderation(
                    mod.queue.community,
                    mod.queue,
                    senior=True,
                )
                expire_and_delete(mod)
        moderator_exclude: List[int] = list(
            Moderation.objects.filter(queue=mod.queue)
            .values_list('moderator__id', flat=True)
            .order_by('moderator__id').distinct('moderator')
        )
        logger.debug(f"moderator_exclude: {moderator_exclude}")
        create_moderation(
            mod.queue.community,
            mod.queue,
            exclude=moderator_exclude,
            senior=False,
        )
        expire_and_delete(mod)
        
def expire_and_delete(moderation):
        try:
            state = CategoryMetadata.objects.get(name='expired')
        except CategoryMetadata.DoesNotExist:
            state = None
        moderation.state = state
        moderation.save()
        moderation.delete()

@shared_task   
def handle_viral_moderation(socialuser_id):
    viral_moderation(socialuser_id, cached=False)

"""handle_accept_follower

Process newly categorized social user to check if they should be allowed
in as follower by protected social media accounts.

ucr: pk of UserCategoryRelationship instance
"""
@shared_task
def handle_accept_follower(ucr_pk: int):
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
        domain: str
    ):
    if not screen_name:
        return
    api = get_api()
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
        
    
    