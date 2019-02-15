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
                "label": "Red Bird",
                "description": "A description about the red bird.",
                "metadata": "external_id_1"
             }
    logger.debug(f"Category.objects.all(): {Category.objects.all()}")
    for cat in Category.objects.all():
        opt = dict(option)
        opt["label"] = cat.label_fr
        opt["description"] = cat.label_en
        opt["metadata"] = f"moderation_{id}_{cat.name}"
        options.append(opt)

    qr["options"] = options
    logger.debug(f"qr: {qr}")
    return qr