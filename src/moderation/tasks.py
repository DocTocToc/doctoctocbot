from unicodedata import category

from versions.exceptions import DeletionOfNonCurrentVersionError

from doctocnet.celery import app
from bot.tasks import handle_retweet
from .profile import twitterprofile
from moderation.lists.poll import poll_lists_members, create_update_lists
from django.conf import settings
from conversation.utils import screen_name

from django.db import transaction, DatabaseError
from dm.models import DirectMessage
from moderation.models import Moderation, SocialUser, Category, UserCategoryRelationship
import os

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@app.task
def handle_backup_lists():
    from .lists.poll import backup_lists
    backup_lists()

@app.task
def handle_poll_lists_members():
    poll_lists_members()
    
@app.task
def handle_create_update_lists():
    create_update_lists()

@app.task
def handle_create_update_profile(userid_int):
    from conversation.models import Tweetdj

    try:
        tweetdj_mi = Tweetdj.objects.filter(userid = userid_int).latest()
    except Tweetdj.DoesNotExist:
        tweetdj_mi = None
        
    if tweetdj_mi is None:
        from bot.bin.user import getuser
        userjson = getuser(userid_int)
    else:
        userjson = tweetdj_mi.json.get("user")

    logger.debug(userjson)
    twitterprofile(userjson)

@app.task
def handle_sendmoderationdm(mod_instance_id):
    from .moderate import quickreply
    from .models import Moderation
    from dm.api import senddm
    import time
    
    mod_mi = Moderation.objects.get(pk=mod_instance_id)
    qr = quickreply(mod_instance_id)
    logger.info(f"mod_mi.moderator.user_id: {mod_mi.moderator.user_id}")
    #logger.debug(f"moderator profile: {mod_mi.moderator.profile}")
    mod_mi.refresh_from_db()
    logger.info(f"mod_mi.queue.user_id {mod_mi.queue.user_id}")
    handle_create_update_profile.apply_async(args=(mod_mi.queue.user_id,))
    sn = screen_name(mod_mi.queue.status_id)
    status_id = mod_mi.queue.status_id
    dm_txt = ("Please moderate this user: @{screen_name} "
              "Tweet: https://twitter.com/{screen_name}/status/{status_id}"
              .format(screen_name=sn, status_id=status_id))

    senddm(dm_txt,
           user_id=mod_mi.moderator.user_id,
           return_json=True,
           quick_reply=qr)

@app.task
def poll_moderation_dm():
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

    
    bot_id = settings.BOT_ID
    current_mod_uuids = [str(mod.id) for mod in Moderation.objects.current.all()]
    
    # return if no current Moderation object
    if not current_mod_uuids:
        return
    
    #logger.info(f"current_moderations_uuid_str_lst: {current_moderations_uuid_str_lst}")
    dms = DirectMessage.objects\
        .filter(recipient_id=bot_id)\
        .filter(jsn__kwargs__message_create__message_data__quick_reply_response__metadata__startswith="moderation")
    logger.info(f"all moderation direct messages answers: {len(dms)} {[dm.text + os.linesep for dm in dms]}")
    #dmsgs_current = [dmsg for dmsg in dmsgs if (dmsg.jsn['kwargs']['message_create']['message_data']['quick_reply_response']['metadata'].split("_")[1] in current_moderations_uuid_str_lst)]

    dms_current = []
    for dm in dms:
        uid = dm.jsn['kwargs']['message_create']['message_data']['quick_reply_response']['metadata'][11:47]
        logger.info(f"uid: {uid}")
        ok = uid in current_mod_uuids
        if ok:
            dms_current.append(dm)
    
    #logger.info(f"current moderation direct messages answers: {len(dms_current)} {[dm.text + os.linesep for dm in dms_current]}")
    for dm in dms_current:
        metadata = dm.jsn["kwargs"]["message_create"]["message_data"]["quick_reply_response"]["metadata"]
        moderation_id = metadata[11:47]
        mod_cat_name = metadata[48:]    
        logger.info(f"dm moderation_id: {moderation_id}, cat: {mod_cat_name}")
        #retrieve moderaton instance
        try:
            mod_mi = Moderation.objects.get(pk=moderation_id)
        except Moderation.DoesNotExist as e:
            logger.error(f"Moderation object with id {moderation_id} "
                         f"does not exist. Error message: {e}")
            continue
        logger.info(f"mod_mi:{mod_mi}")
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
            logger.info(f"moderated_su_mi:{moderated_su_mi}")
            logger.info(f"moderated_su_mi.profile:{moderated_su_mi.profile}")

        except SocialUser.DoesNotExist:
            moderated_su_mi = None
        
        # Category instance
        try:
            cat_mi = Category.objects.get(name=mod_cat_name)
            logger.info(f"cat_mi:{cat_mi}")
        except Category.DoesNotExist:
            cat_mi = None
        
        # moderator SocialUser instance
        try:
            moderator_su_mi = SocialUser.objects.get(user_id=dm.sender_id)
            logger.info(f"moderator_su_mi:{moderator_su_mi}")
        except SocialUser.DoesNotExist:
            moderator_su_mi = None
        
        #Check if relationship already exists
        is_already = None
        all_cat = moderated_su_mi.category.all()
        if all_cat:
            is_already = cat_mi in all_cat
            if is_already:
                logger.info(f"{moderated_su_mi} is already a {cat_mi}")
                delete_moderation_queue(mod_mi)
        
        # create UserCategoryRelationship
        ucr = None
        if (is_current and cat_mi and moderated_su_mi and not is_already):
            with transaction.atomic():
                try:
                    ucr = UserCategoryRelationship.objects.create(
                        social_user = moderated_su_mi,
                        category = cat_mi,
                        moderator = moderator_su_mi)
                except DatabaseError as e:
                    logger.error(e)

        # retweet status if user category is among authorized categories  
        if ucr:
            logger.info(f"ucr creation successful: {ucr}")
            status_id = mod_mi.queue.status_id
            delete_moderation_queue(mod_mi)
            if cat_mi in Category.authorized.all():
                handle_retweet.apply_async(args=(status_id,))

        # TODO: create a cursor based on DM timestamp to avoid processing all DMs during each polling
        # TODO: check that the moderator is following the bot before attempting to send a DM