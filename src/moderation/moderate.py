import logging

from django.db.utils import IntegrityError, DatabaseError
from django.db.models import F
from django.conf import settings
from django.utils.translation import activate

from moderation.models import Queue, Moderation, CategoryMetadata
from moderation.social import update_social_ids
from community.models import Retweet
from conversation.models import Hashtag
from community.models import Community
from community.models import CommunityCategoryRelationship

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
        logger.debug(dct)
        addtoqueue(user_id, status_id, dct['community_name'])

def addtoqueue(user_id, status_id, community_name):
    try:
        community = Community.objects.get(name=community_name)
    except Community.DoesNotExist as e:
        logger.error(e)
        return
    try:
        Queue.objects.create(
            user_id = user_id,
            status_id = status_id,
            community = community
        )
    except DatabaseError as e:
        logger.error(e)

def quickreply(moderation_instance_id):
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
        moderation_instance=Moderation.objects.get(id=moderation_instance_id)
    except Moderation.DoesNotExist:
        return
    community=moderation_instance.queue.community
    if community.language:
        activate(community.language)
    for ccr in CommunityCategoryRelationship.objects.filter(
        quickreply=True,
        community=community
        ):
        logger.debug(f"Category name: {ccr.category.name}")
        opt = dict(option)
        opt["label"] = ccr.category.label
        opt["metadata"] = f"moderation{moderation_instance_id}{ccr.category.name}"
        opt["description"] = ccr.category.description or ccr.category.label
        options.append(opt)
    
    for cm in CategoryMetadata.objects.filter(dm=True):
        opt = dict(option)
        opt["label"] = cm.label
        opt["metadata"] = f"moderation{moderation_instance_id}{cm.name}"
        opt["description"] = cm.description
        options.append(opt)
    qr["options"] = options
    logger.debug(f"qr: {qr}")
    return qr

