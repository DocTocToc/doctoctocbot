import logging

from django.db.utils import IntegrityError, DatabaseError
from django.db.models import F
from django.conf import settings

from moderation.models import Queue
from moderation.social import update_followersids
from community.models import Retweet
from conversation.models import Hashtag
from community.models import Community

logger = logging.getLogger(__name__)

def process_unknown_user(user_id, status_id, hrh):
    logger.debug("processing unknown user")
    dct_lst = Retweet.objects.filter(retweet=True) \
                                .filter(hashtag__in=hrh.hashtag_mi_lst) \
                                .values(
                                    community_name=F('community__name'),
                                    username=F('community__account__username')
                                ) \
                                .distinct()
    for dct in dct_lst:
        try:
            community = Community.objects.get(name=dct['community_name'])
        except Community.DoesNotExist:
            continue
        bot_screen_name = community.account.username
        follower_id_lst = update_followersids(dct['username'], cached=False, bot_screen_name=bot_screen_name)
        if not follower_id_lst:
            logger.warn(f"{dct['username']} does not have any followers.")
            continue
        if user_id in follower_id_lst:
            addtoqueue(user_id, status_id, dct['community_name'])

def addtoqueue(user_id, status_id, community_name):
    try:
        community = Community.objects.get(name=community_name)
    except Community.DoesNotExist as e:
        logger.error(e)   
    try:
        Queue.objects.create(user_id = user_id,
                             status_id = status_id,
                             community = community)
    except DatabaseError as e:
        logger.error(e)

def quickreply(id):
    from .models import Category
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
        
    for cat in Category.objects.filter(quickreply=True):
        logger.debug(f"Category name: {cat.name}")
        opt = dict(option)
        opt["label"] = cat.label
        opt["metadata"] = f"moderation{id}{cat.name}"
        opt["description"] = cat.description or cat.label
        options.append(opt)

    qr["options"] = options
    logger.debug(f"qr: {qr}")
    return qr