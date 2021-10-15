import uuid
import logging
import random
import os
from typing import Optional, List
from dm.models import DirectMessage
from moderation.models import (
    Moderation,
    SocialUser,
    Category,
    UserCategoryRelationship,
    CategoryMetadata,
    Queue,
    ModerationOptIn,
    Moderator,
)
from community.models import CommunityCategoryRelationship
from optin.models import Option, OptIn
from bot.tasks import handle_triage_status
from django.db import transaction, DatabaseError
from django.utils.translation import gettext as _
from moderation.social import send_graph_dm
from moderation.profile import create_update_profile
from dm.api import senddm
from community.helpers import (
    get_community_bot_screen_name,
    activate_language,
)
from conversation.utils import screen_name

logger = logging.getLogger(__name__)

class CommunityProcessor:
    def __init__(self, community):
        self.community = community
        self.bot_user_id = self.get_bot_user_id()
        self.dm: List[DirectMessage] = self.get_dm()
        self.current_mod_uuid: List[uuid.UUID] = self.get_current_mod_uuid()

    def get_bot_user_id(self):
        account = self.community.account
        if not account:
            logger.error(f"Community {self.community} not linked to any account.")
            return
        bot_user_id = account.userid
        if not bot_user_id:
            logger.error(f"{account=} object userid field is null")
        return bot_user_id

    def get_dm(self):
        return DirectMessage.objects \
            .filter(recipient_id=self.bot_user_id) \
            .filter(jsn__quick_reply_response__metadata__startswith="moderation")

    def get_current_mod_uuid(self):
        return Moderation.objects.current.filter(
            state=None,
            queue__community=self.community,
        ).values_list("id", flat=True)

    def process(self):
        for dm in self.dm:
            dmp = DirectMessageProcessor(dm)
            if dmp.moderation_uuid in self.current_mod_uuid:
                mp = ModerationProcessor(dmp)
                if dmp.category:
                    mp.add_category()
                elif dmp.meta_category:
                    mp.process_meta_category()

class ModerationProcessor:
    def __init__(self, dmp):
        self.dmp = dmp
        self.moderation = dmp.get_moderation()
        self.moderated: SocialUser = self.get_moderated()
        self.moderator = self.moderation.moderator
        self.community = self.moderation.queue.community

    def get_moderated(self):
        try:
            return SocialUser.objects.get(
                user_id=self.moderation.queue.user_id
            )
        except SocialUser.DoesNotExist:
            return

    def add_category(self):
        with transaction.atomic():
            try:
                ucr = UserCategoryRelationship.objects.create(
                    social_user = self.moderated,
                    category = self.dmp.category,
                    moderator = self.moderator,
                    community = self.community
                )
                self.set_moderation_state('done')
            except DatabaseError as e:
                logger.error(e)
                ucr = None
        if ucr:
            # if queue created following status, triage status for RT
            if self.moderation.queue.status_id:
                handle_triage_status.apply_async(
                    args=(self.moderation.queue.status_id, self.community.name)
                )
            # if viral moderation, add newly moderated to moderator
            if self.community.viral_moderation:
                viral_moderation(self.moderated.id)

    def set_moderation_state(self, cat_meta_name):
        try:
            cm = CategoryMetadata.objects.get(name=cat_meta_name)
        except CategoryMetadata.DoesNotExist:
            logger.error(
                f"CategoryMetadata has no instance named '{cat_meta_name}'"
            )
            return
        with transaction.atomic():
            self.moderation.state = cm
            self.moderation.save()
            self.moderation.delete()

    def  process_meta_category(self):
        meta_cat = self.dmp.meta_category.name
        if meta_cat=='stop':
            if self.process_meta_stop():
                self.set_moderation_state('stop')
        elif meta_cat=='fail':
            self.set_moderation_state('fail')
            moderation = create_moderation(
                self.community,
                self.moderation.queue,
                senior=True,
            )
            sendmoderationdm(moderation)
        elif meta_cat=='busy':
            self.set_moderation_state('busy')
            moderation = create_moderation(
                self.community,
                self.moderation.queue,
                exclude=self.moderator,
                senior=False,
            )
            sendmoderationdm(moderation)

    def process_meta_stop(self):
        if self.moderation.queue.type in [Queue.SELF, Queue.FOLLOWER]:
            if self.process_moderation_optin():
                self.set_moderation_state('stop')
        elif self.moderation.queue.type == Queue.MODERATOR:
            if self.inactivate_moderator():
                moderation = create_moderation(
                    self.community,
                    self.moderation.queue,
                )
                sendmoderationdm(moderation)
        # if STOP answer comes from dev or senior, consider it as mistake
        elif self.moderation.queue.type in [Queue.DEVELOPER, Queue.SENIOR]:
            logger.error(
                "Developer or Senior moderators cannot give up moderation!"
            )

    def process_moderation_optin(self):
        queue_type = self.moderation.queue.type
        try:
            option = Option.objects.get(
                name=f'twitter_dm_moderation_{queue_type}'
            )
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
            socialuser=self.moderator
        ).first()
        if optin:
            optin = optin.clone()
            optin.authorize=mod_optin.authorize
            optin.save()
            return True
        else:
            try:
                OptIn.objects.create(
                    option=option,
                    socialuser=self.moderator,
                    authorize=mod_optin.authorize   
                )
                return True
            except DatabaseError as e:
                logger.error(f"OptIn not created for {self.moderation}: {e}")
                return

    def inactivate_moderator(self):
        moderator_mi = self.moderator.moderator.filter(
            community=self.community
        ).first()
        if not moderator_mi.active:
            return True
        else:
            moderator_mi.public=False
            moderator_mi.active=False
            moderator_mi.save()
            return True


class DirectMessageProcessor:
    def __init__(self, dm: DirectMessage):
        self.dm: DirectMessage = dm
        self.metadata: str = self.get_metadata()
        self.moderation_uuid: uuid.UUID = self.get_moderation_uuid()
        self.category: Optional[Category] = self.get_category()
        self.meta_category: Optional[CategoryMetadata] = self.get_meta_category()

    def get_metadata(self):
        try:
            return self.dm.jsn['kwargs']['message_create']['message_data']['quick_reply_response']['metadata']
        except:
            try:
                return self.dm.jsn['quick_reply_response']['metadata']
            except:
                logger.error(f"no metadata could be retrieved from DM {self.dm}")

    def get_moderation_uuid(self):
            uuid_str = self.metadata[10:46]
            if not uuid_str:
                logger.error(f"no uuid string could be retrieved from DM {self.dm}")
                return
            try:
                moderation_uuid = uuid.UUID(uuid_str)
            except ValueError as e:
                logger.error(f"no valid uuid could be retrieved from DM {self.dm}: {e}")
                return
            return moderation_uuid

    def get_category(self):
        try:
            return Category.objects.get(name=self.metadata[46:])
        except Category.DoesNotExist:
            return

    def get_meta_category(self):
        try:
            return CategoryMetadata.objects.get(name=self.metadata[46:])
        except CategoryMetadata.DoesNotExist:
            return
        
    def get_moderation(self):
        try:
            return Moderation.objects.get(id=self.moderation_uuid)
        except Moderation.DoesNotExist as e:
            logger.error(
                f"Moderation object with id {self.moderation_uuid} "
                f"does not exist.\nError message: {e}"
                )

  
def sendmoderationdm(mod_mi):
    logger.debug(f'inside sendmoderationdm({mod_mi=})')
    bot_screen_name = get_community_bot_screen_name(
        mod_mi.queue.community
    )
    create_update_profile(
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
    qr = quickreply(mod_mi)
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
        return new_mod_mi
    except:
        return

def viral_moderation(socialuser_id, cached=True):
    """ Once categorized, a social user belonging to an approved category
    becomes a moderator.
    """
    ucr_qs = UserCategoryRelationship.objects.filter(
        social_user__id = socialuser_id ,
        community__in = Community.objects.filter(viral_moderation=True)
    )
    logger.debug(ucr_qs)
    for ucr in ucr_qs:
        if ucr.category in ucr.community.viral_moderation_category.all():
            if not Moderator.objects.filter(
                socialuser=ucr.social_user,
                community=ucr.community,
            ).exists():
                followers = update_social_ids(
                    ucr.community.account.userid,
                    cached=cached,
                    bot_screen_name=ucr.community.account.username,
                    relationship='followers',
                )
                if not followers:
                    return
                if ucr.social_user.user_id in followers:
                    try:
                        Moderator.objects.create(
                            socialuser = ucr.social_user,
                            active = True,
                            public = False,
                            community = ucr.community,
                        )
                        logger.debug(
                            f"{ucr.social_user} added to Moderator"
                        )
                    except DatabaseError:
                        continue
                    msg = ucr.community.viral_moderation_message
                    if msg:
                        res = senddm(
                            msg,
                            user_id=ucr.social_user.user_id,
                            screen_name=ucr.community.account.username,
                        )
                        handle_twitter_dm_response(
                            res,
                            socialuser_id,
                            ucr.community.id,
                        )
                    return True
                else:
                    logger.debug(
                        f"{ucr.social_user} is not following "
                        f"@{ucr.community.account.username}"
                    )

def handle_twitter_dm_response(res, moderator_su_id, community_id):
    """ treat DM errors
    if error is one ot those
    {"errors": [{"code": 326, "message": "You are sending a Direct Message to users that do not follow you."}]}
    {"errors": [{"code": 349, "message": "You cannot send messages to this user."}]}
    {"errors": [{"code": 150, "message": "You cannot send messages to users who are not following you."}]}
    """
    if not res:
        return
    if not isinstance(res, dict):
        res = ast.literal_eval(res)
    if not "errors" in res.keys():
        return
    for error in res["errors"]:
        if error.get("code") in [150, 326, 349]:
            moderator_mi = (
                Moderator.objects
                .filter(
                    socialuser__id = moderator_su_id,
                    community__id = community_id
                ).first()
            )
            if moderator_mi:
                moderator_mi.active = False
                moderator_mi.public = False
                moderator_mi.save()

def quickreply(moderation_instance):
    qr = {
           "type": "options",
           "options": []
          }
    options = []
    option = {
                "label": "?",
                "description": "?",
                "metadata": "?"
             }
    try:
        community=moderation_instance.queue.community
    except:
        community=None
    if community:
        activate_language(community)
    if moderation_instance.queue.type == Queue.SELF:
        ccr_qs = CommunityCategoryRelationship.objects.filter(
            quickreply_self=True,
            community=community
        )
    else:
        ccr_qs = CommunityCategoryRelationship.objects.filter(
            quickreply=True,
            community=community
        )
    for ccr in ccr_qs:
        logger.debug(f"Category name: {ccr.category.name}")
        opt=dict(option)
        opt["label"]=ccr.category.label
        opt["metadata"]=f"moderation{moderation_instance.id}{ccr.category.name}"
        opt["description"]=ccr.category.description or ccr.category.label
        options.append(opt)

    if moderation_instance.queue.type == Queue.SELF:
        cat_meta = CategoryMetadata.objects.filter(self_dm=True)
    else:
        cat_meta = CategoryMetadata.objects.filter(dm=True)

    for cm in cat_meta:
        opt = dict(option)
        opt["label"] = cm.label
        opt["metadata"] = f"moderation{moderation_instance}{cm.name}"
        opt["description"] = cm.description
        options.append(opt)
    qr["options"] = options
    logger.debug(f"{qr=}")
    return qr