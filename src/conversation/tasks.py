import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def handle_normalize(statusid):
    from .utils import normalize
    normalize(statusid)
    

@shared_task
def handle_allnormalize():
    from .utils import allnormalize
    allnormalize()


@shared_task
def handle_update_trees(hourdelta):
    from .utils import update_trees
    update_trees(hourdelta)
    

@shared_task
def handle_addsocialuser():
    from moderation.models import addsocialuser
    from conversation.models import Tweetdj
    for instance in Tweetdj.objects.all():
        addsocialuser(instance)

        
@shared_task
def handle_get_physician_timeline():
    from bot.bin.timeline import record_user_timeline
    from moderation.models import SocialUser
    for user_id in SocialUser.objects.physician_users():
        record_user_timeline(user_id)