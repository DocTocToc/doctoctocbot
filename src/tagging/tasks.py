import os
import unidecode
from typing import Optional, List

from django.utils.translation import gettext as _
from django.db import transaction, DatabaseError
from django.urls import reverse

from celery.utils.log import get_task_logger
from versions.exceptions import DeletionOfNonCurrentVersionError

from tagging.models import Process, Queue, Category
from dm.api import senddm
from celery import shared_task
from conversation.models import Tweetdj
from moderation.models import SocialMedia, SocialUser
from community.models import Community
from community.helpers import site_url
from dm.models import DirectMessage
from optin.authorize import has_authorized, create_opt_in
from optin.models import Option
from tagging.models import TagKeyword, Category
from bot.tweet import hashtag_list
from community.helpers import activate_language

logger = get_task_logger(__name__)

CATEGORY_TAG = "category"
UUID_LENGTH = 36
OPTIN_OPTION = "twitter_dm_category_self"
STOP_CATEGORY = "stop"

def get_optin_option() -> Optional[Option]:
    try:
        option = Option.objects.get(name=OPTIN_OPTION)
    except Option.DoesNotExist:
        logger.error(f"Option {OPTIN_OPTION} is not present in the database.")
        option = None
    return option

def quickreply(process_id):
    try:
        process = Process.objects.get(id=process_id)
    except Process.DoesNotExist:
        return
    category_lst = Category.objects.filter(community=process.queue.community)
    if not category_lst:
        return
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
    for cat in category_lst:
        opt = dict(option)
        hash = lambda: "#" if cat.hashtag else ""
        opt["label"] = f"{hash()}{cat.tag}"
        opt["description"] = cat.summary or cat.tag
        opt["metadata"] = f"{CATEGORY_TAG}{process.id}{cat.tag}"
        options.append(opt)

    qr["options"] = options
    logger.debug(f"qr: {qr}")
    return qr



def tag_dm_text(process):
    process.refresh_from_db()
    statusid = process.queue.uid
    try:
        tweetdj = Tweetdj.objects.get(statusid=statusid)
    except Tweetdj.DoesNotExist as e:
        logger.warn(e)
        return
    activate_language(process.community)    
    # underscore will be replaced by Twitter with the screen name of the user
    screen_name = tweetdj.socialuser.screen_name_tag() or "_"
    logger.debug(screen_name)
    categories_link = f"{site_url(process.queue.community)}{reverse('landing:categories')}"
    text = (
        _(
            "Please help us find the best category for this tweet "
            "https://twitter.com/{screen_name}/status/{statusid}\n"
            "Please choose a category by clicking on one of the buttons bellow.\n"
            "Categories are described in full detail on this page ➡️ "
            "{categories_link}"
        ).format(
            screen_name=screen_name,
            statusid=statusid,
            categories_link=categories_link
        )
    )
    logger.debug(text)
    return text

def send_tag_dm(process, user_id):
    logger.info(f"process.processor.id: {process.processor.id}")

    response = senddm(
        tag_dm_text(process),
        user_id=user_id,
        screen_name=process.queue.community.account.username,
        return_json=True,
        quick_reply=quickreply(process.id)
    )
    logger.info(response)
    return response


@shared_task(bind=True)
def send_tag_request(self, process_id, user_id):
    process_mi = Process.objects.get(id=process_id)
    if process_mi.queue.socialmedia.name == "twitter":
        response = send_tag_dm(process_mi, user_id)
        try:
            response["event"]["created_timestamp"]
        except KeyError:
            self.retry(countdown= 2 ** self.request.retries)

@shared_task            
def handle_create_tag_queue(statusid, socialmedia_id, community_id):
    logger.debug(f"handle_create_tag_queue({statusid}, {socialmedia_id}, {community_id})")
    
    try:
        socialmedia = SocialMedia.objects.get(id=socialmedia_id)
    except SocialMedia.DoesNotExist as e:
        logger.warn(e)
        return
    logger.debug(socialmedia)
    
    try:
        community = Community.objects.get(id=community_id)
    except Community.DoesNotExist as e:
        logger.warn(e)
        return
    logger.debug(community)
    
    if not Category.objects.filter(community=community).exists():
        logger.warn("There are no tagging categories for this community.")
        return
    
    try:
        tweetdj = Tweetdj.objects.get(statusid=statusid)
    except Tweetdj.DoesNotExist:
        return
    
    category_tags = list(
        Category.objects.filter(
            community=community,
            hashtag=True,
        ).values_list('tag', flat=True)
    )
    logger.debug(f"{category_tags}")
    
    tweet_tags = tweetdj.tags.names()
    logger.debug(f"{tweet_tags}")
    
    # if status does not have any tags corresponding to a category,
    # create queue
    logger.debug(f"{set(category_tags).isdisjoint(tweet_tags)}")
    if set(category_tags).isdisjoint(tweet_tags):
        queue, created = Queue.objects.get_or_create(
                uid=statusid,
                socialmedia=socialmedia,
                community=community
        )
        if created:
            logger.info("Queue created.")
            create_tag_process(queue, statusid)

def create_tag_process(queue, statusid):
    try:
        tweetdj = Tweetdj.objects.get(statusid=statusid)
    except Tweetdj.DoesNotExist as e:
        logger.warn(e)
        return
    socialuser = tweetdj.socialuser
    if not socialuser:
        logger.debug("No SocialUser")
        return
    option = get_optin_option()
    has_opted_in = has_authorized(socialuser, option)
    logger.debug(f"_has_authorized: {has_opted_in}")
    # If Opt in not yet set for this user, create it as True
    if has_opted_in is None:
        create_opt_in(socialuser, option, authorize=True)
    if has_authorized(socialuser, option):
        process, created = Process.objects.get_or_create(
            queue=queue,
            processor=socialuser
        )
        if created:
            logger.info("Process created.")
            send_tag_request.apply_async(args=(process.id, socialuser.user_id))
                    
        
@shared_task
def poll_tag_dm():
    def delete_tag_queue(process_mi):
        with transaction.atomic():
            try:
                process_mi.queue.delete()
            except DeletionOfNonCurrentVersionError as e:
                logger.info(f"Queue {process_mi.queue} was already deleted. %s" % e)
        delete_tag_process(process_mi)

    def delete_tag_process(process_mi):
        with transaction.atomic():
            try:
                process_mi.delete()
            except DeletionOfNonCurrentVersionError as e:
                logger.info(f"Tag process instance {process_mi} was already processed. %s" % e)

    def get_tag_metadata(dm):
        return dm.jsn['kwargs']['message_create']['message_data']['quick_reply_response']['metadata']
    
    def get_process_id(dm):
        begin_idx = len(CATEGORY_TAG)
        end_idx = len(CATEGORY_TAG) + UUID_LENGTH 
        return get_tag_metadata(dm)[begin_idx:end_idx]
    
    def get_tag_name(dm):
        end_idx = len(CATEGORY_TAG) + UUID_LENGTH
        return get_tag_metadata(dm)[end_idx:]
    
    def tag(process_mi, tag_name):
        # determine id of status
        status_id = process_mi.queue.uid
        # Tweetdj
        try:
            tweetdj = Tweetdj.objects.get(statusid=status_id)
            logger.info(f"tweetdj:{tweetdj}")
        except Tweetdj.DoesNotExist:
            return
        #taggit
        logger.info(f"Adding tag '{tag_name}' to {tweetdj}")
        tweetdj.tags.add(tag_name)
        delete_tag_queue(process_mi)

    current_process_uuid_lst = [str(process.id) for process in Process.objects.current.all()]
    logger.debug(f"current_process_uuid_lst: {current_process_uuid_lst}")
    # return if no current Moderation object
    if not current_process_uuid_lst:
        return
    
    bot_id_lst = Community.objects.values_list("account__userid", flat=True)
    dms = DirectMessage.objects\
        .filter(recipient_id__in=bot_id_lst)\
        .filter(jsn__kwargs__message_create__message_data__quick_reply_response__metadata__startswith=CATEGORY_TAG)
    logger.info(f"all {CATEGORY_TAG} direct messages answers: {len(dms)} {[dm.text + os.linesep for dm in dms]}")
    #dmsgs_current = [dmsg for dmsg in dmsgs if (dmsg.jsn['kwargs']['message_create']['message_data']['quick_reply_response']['metadata'].split("_")[1] in current_moderations_uuid_str_lst)]

    dms_current = []
    for dm in dms:
        uid = get_process_id(dm)
        logger.info(f"uid: {uid}")
        ok = uid in current_process_uuid_lst
        logger.info(f"ok = uid in current_process_uuid_lst: {ok}")
        if ok:
            dms_current.append(dm)
    
    for dm in dms_current:
        process_id = get_process_id(dm)
        tag_name = get_tag_name(dm)
        logger.info(f"dm process_id: {process_id}, cat: {tag_name}")
        #retrieve moderation instance
        try:
            process_mi = Process.objects.get(pk=process_id)
        except Process.DoesNotExist as e:
            logger.error(f"Process object with id {process_id} "
                         f"does not exist. Error message: {e}")
            continue
        logger.info(f"process_mi:{process_mi}")
        # if mod_mi is not the current version, current_version() returns None
        # and it means this moderation was already done and we pass
        is_current = bool(Process.objects.current_version(process_mi))
        if not is_current:    
            logger.info(f"Process instance {process_mi} was already processed.")
            continue
        
        socialuser = process_mi.processor
        
        if tag_name == STOP_CATEGORY:
            opt_out(socialuser)
            delete_tag_process(process_mi)
        else:
            tag(process_mi, tag_name)
        
def opt_out(socialuser):
    option = get_optin_option()
    create_opt_in(socialuser=socialuser, option=option, authorize=False)
    
def keyword_tag(statusid, community):
    def category_tagging(tweetdj, community, hashtag):
        tags = diacriticless_category_tags(community)
        if hashtag:
            for tag in tags:
                if tag in hashtag:
                    tweetdj.tags.add(tag)
    def keyword_tagging(tweetdj, community, hashtag):
        qs = TagKeyword.objects.filter(community__in=[community]).distinct()
        for tk in qs:
            if hashtag:
                for tag_name in tk.tag.names():
                    if tag_name in hashtag:
                        tweetdj.tags.add(tag_name)
            for keyword in tk.keyword:
                if keyword in tweetdj.json["full_text"].lower():
                    for tag_name in tk.tag.names():
                        tweetdj.tags.add(tag_name)
    try:
        tweetdj = Tweetdj.objects.get(statusid=statusid)
    except Tweetdj.DoesNotExist:
        return
    hashtag: List = hashtag_list(tweetdj.json)
    category_tagging(tweetdj, community, hashtag)
    keyword_tagging(tweetdj, community, hashtag)

def diacriticless_category_tags(community):
    # return a list of all category tags of a community, without diacritic,
    # lowercased
    tags = Category.objects.filter(
        community=community,
        hashtag=True,
    ).values_list('tag', flat=True)
    return [unidecode.unidecode(tag).lower() for tag in tags]    