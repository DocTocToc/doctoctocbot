import logging

from django.db.utils import IntegrityError
from django.conf import settings

from moderation.models import Queue
from moderation.social import update_followersids

logger = logging.getLogger(__name__)

def process_unknown_user(user_id, status_id):
    if user_id in update_followersids(settings.BOT_ID):
        addtoqueue(user_id, status_id)

def addtoqueue(user_id, status_id):
    q = Queue.objects.create(user_id = user_id, status_id = status_id)
    try:
        q.save()
    except IntegrityError:
        logging.exception('')
        return

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