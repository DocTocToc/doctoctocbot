import logging
from doctocnet.celery import app

logger = logging.getLogger(__name__)

@app.task
def handle_normalize(statusid):
    from .utils import normalize
    normalize(statusid)
    
@app.task
def handle_allnormalize():
    from .utils import allnormalize
    allnormalize()

@app.task
def handle_update_trees(hourdelta):
    from .utils import update_trees
    update_trees(hourdelta)
    
@app.task
def handle_addsocialuser():
    from moderation.models import addsocialuser
    from conversation.models import Tweetdj
    for instance in Tweetdj.objects.all():
        addsocialuser(instance)

@app.task        
def handle_get_physician_timeline():
    from bot.bin.timeline import record_user_timeline
    from moderation.models import SocialUser
    for user_id in SocialUser.objects.physician_users():
        record_user_timeline(user_id)
        

        