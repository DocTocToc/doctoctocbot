import random, logging

from .models import Queue, SocialUser
from django.db.utils import IntegrityError

def addtoqueue(userid, statusid):
    chosenmoderatorid_int = random.choice(SocialUser.objects.moderators())
    moderator_mi = SocialUser.objects.get(user_id = chosenmoderatorid_int)
    q = Queue.objects.create(user_id = userid,
                         status_id = statusid,
                         moderator = moderator_mi)
    try:
        q.save()
    except IntegrityError:
        logging.exception('')
        return
    # launch asynchronous moderation task
    return
            