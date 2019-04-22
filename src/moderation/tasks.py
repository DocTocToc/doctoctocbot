import logging
from logging.handlers import RotatingFileHandler
from unicodedata import category

from versions.exceptions import DeletionOfNonCurrentVersionError

from doctocnet.celery import app
from bot.tasks import handle_retweet
from .profile import twitterprofile
from moderation.lists.poll import poll_lists_members, create_update_lists
from django.conf import settings
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

from celery.signals import after_setup_logger, after_setup_task_logger

@after_setup_task_logger.connect
def after_setup_celery_task_logger(logger, **kwargs):
    """ This function sets the 'celery.task' logger handler and formatter """
    create_celery_logger_handler(logger, True)


@after_setup_logger.connect
def after_setup_celery_logger(logger, **kwargs):
    """ This function sets the 'celery' logger handler and formatter """
    create_celery_logger_handler(logger, False)

def create_celery_logger_handler(logger, propagate):
    # 209715200 is 1024 * 1024 * 200 or 200 MB, same as in settings
    celery_handler = RotatingFileHandler(
        settings.CELERY_LOG_FILE,
        maxBytes=209715200,
        backupCount=10
    )
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    #celery_formatter = jsonlogger.JsonFormatter(settings.LOGGING['formatters']['json']['format'])
    celery_handler.setFormatter(formatter)

    logger.addHandler(celery_handler)
    logger.logLevel = settings.LOG_LEVEL
    logger.propagate = propagate

"""
@after_setup_task_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # SysLogHandler
    slh = logging.handlers.SysLogHandler()
    slh.setFormatter(formatter)
    logger.addHandler(slh)
    # StreamHandler
    str = logging.StreamHandler()
    str.setFormatter(formatter)
    logger.addHandler(str)
    
    logger.logLevel = settings.LOG_LEVEL
"""

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
    screen_name = mod_mi.queue.screen_name_tag()
    counter = 0
    # TODO use chained celery tasks or calbacks instead of this loop
    while screen_name is None and counter < 20:
            mod_mi.refresh_from_db()
            screen_name = mod_mi.queue.screen_name_tag()
            logger.debug("waiting for screen_name...%s" % counter)
            time.sleep(1)
            counter+=1
    status_id = mod_mi.queue.status_id
    dm_txt = ("Please moderate this user: @{screen_name} "
              "Tweet: https://twitter.com/statuses/{status_id}"
              .format(screen_name=screen_name, status_id=status_id))

    senddm(dm_txt,
           user_id=mod_mi.moderator.user_id,
           return_json=True,
           quick_reply=qr)
@app.task
def poll_moderation_dm():
    from django.db import transaction
    from dm.models import DirectMessage
    from moderation.models import Moderation, SocialUser, Category, UserCategoryRelationship
    from django.conf import settings

    bot_id = settings.BOT_ID
    #sender_id_lst = Moderation.objects.as_of().values('moderator')
    #logger.debug(f"sender_id_lst: {sender_id_lst}")
    #sender_id_lst1 = SocialUser.objects.filter(user_id__in=sender_id_lst).values('user_id')
    #logger.debug(f"sender_id_lst1: {sender_id_lst1}")
    sender_id_lst = [mod_mi.moderator.user_id for mod_mi in Moderation.objects.current.all()]
    logger.debug(f"sender_id_lst: {sender_id_lst}")
    uid_lst = list(SocialUser.objects.filter(user_id__in=sender_id_lst).values_list('user_id', flat=True))
    #su_dict = SocialUser.objects.in_bulk(sender_id_lst)
    #uid_lst = list(su_dict[k].user_id for k in su_dict.keys())
    #logger.debug(f"su: {su_dict}")
    logger.debug(f"uid_lst: {uid_lst}")
    #logger.debug({type(uid_lst[0])})

    #dmsgs0 = DirectMessage.objects.filter(recipient_id=bot_id)
    #dmsgs1 = DirectMessage.objects.filter(recipient_id=bot_id).filter(sender_id__in=uid_lst)
    dmsgs = DirectMessage.objects\
        .filter(recipient_id=bot_id)\
        .filter(sender_id__in=uid_lst)\
        .filter(jsn__kwargs__message_create__message_data__quick_reply_response__metadata__startswith="moderation_")
        
    for dmsg in dmsgs:
        metadata = dmsg.jsn["kwargs"]["message_create"]["message_data"]["quick_reply_response"]["metadata"]
        moderation_id, mod_cat_name = metadata[11:].split("_")    
        logger.debug(f"dmsg id:{moderation_id}, cat: {mod_cat_name}")
        #retrieve moderaton instance
        mod_mi = Moderation.objects.get(pk=moderation_id)
        # if mod_mi is not the current version, current_version() returns None
        # and it means this moderation was already done and we pass
        if not Moderation.objects.current_version(mod_mi):
            logger.info(f"Moderation instance {mod_mi} was already moderated.")
            continue
        logger.debug(f"mod_mi:{mod_mi}")
        # determine id of moderated user
        su_id_int = mod_mi.queue.user_id
        
        # moderated SocialUser instance
        try:
            moderated_su_mi = SocialUser.objects.get(user_id=su_id_int)
            logger.debug(f"moderated_su_mi:{moderated_su_mi}")
            logger.debug(f"moderated_su_mi.profile:{moderated_su_mi.profile}")

        except SocialUser.DoesNotExist:
            continue
        
        # Category instance
        try:
            cat_mi = Category.objects.get(name=mod_cat_name)
            logger.debug(f"cat_mi:{cat_mi}")
        except Category.DoesNotExist:
            continue
        
        # moderator SocialUser instance
        try:
            moderator_su_mi = SocialUser.objects.get(user_id=dmsg.sender_id)
            logger.debug(f"moderator_su_mi:{moderator_su_mi}")
        except SocialUser.DoesNotExist:
            continue
        
        #Check if relationship already exists
        if cat_mi in moderated_su_mi.category.all():
            logger.debug(f"{moderated_su_mi} is already a {cat_mi}")
            return
        
        # create UserCategoryRelationship
        with transaction.atomic():
            UserCategoryRelationship.objects.create(
                social_user = moderated_su_mi,
                category = cat_mi,
                moderator = moderator_su_mi)
            
        logger.debug(f"moderated user categories: {moderated_su_mi.category.all()}")
        
        # retweet status if user category is among authorized categories
        if cat_mi in Category.authorized.all():
            handle_retweet.apply_async(args=(mod_mi.queue.status_id,))
        
        if cat_mi in moderated_su_mi.category.all():
            with transaction.atomic():
                try:
                    mod_mi.queue.delete()
                    mod_mi.delete()
                except DeletionOfNonCurrentVersionError as e:
                    logger.info(f"Moderation instance {mod_mi} was already moderated. %s" % e)
                    
            
        # TODO: create a cursor based on DM timestamp to avoid processing all DMs during each polling
        # TODO: check that the moderator is following the bot before attempting to send a DM