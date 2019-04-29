from django.db.utils import IntegrityError
import logging  # , random

from .models import Queue  # , SocialUser


logger = logging.getLogger(__name__)

def addtoqueue(sjson):
    q = Queue.objects.create(user_id = sjson["user"]["id"], status_id = sjson["id"])
    try:
        q.save()
    except IntegrityError:
        logging.exception('')
        return
    # launch asynchronous moderation task
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