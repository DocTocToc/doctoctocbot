import logging
import ast
from django.db.utils import IntegrityError, DatabaseError
from django.db.models import F
from django.conf import settings
from django.utils.translation import activate

from moderation.models import (
    Queue,
    Moderation,
    CategoryMetadata,
    Moderator,
    UserCategoryRelationship,
)
from moderation.social import update_social_ids
from community.models import Retweet
from conversation.models import Hashtag
from community.models import Community
from community.models import CommunityCategoryRelationship
from community.helpers import activate_language


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
    # Is there already a queue for this user and this community?
    if Queue.objects.current.filter(
        user_id = user_id,
        community = community,
    ).exists():
        logger.info(
            f"Current queue for user {user_id} with {community} exists."
        )
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
    try:
        community=moderation_instance.queue.community
    except:
        community=None
    if community:
        activate_language(community)

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

def handle_twitter_dm_response(res, moderator_su_id, community_id):
    """ treat DM errors
    if error is one ot those
    {"errors": [{"code": 326, "message": "You are sending a Direct Message to users that do not follow you."}]}
    {"errors": [{"code": 349, "message": "You cannot send messages to this user."}]}
    {"errors": [{"code": 150, "message": "You cannot send messages to users who are not following you."}]}
    """
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
            
        
        
        