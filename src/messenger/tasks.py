from django.utils.formats import localize
from django.conf import settings
from doctocnet.celery import app
from moderation.models import SocialUser, Follower
from messenger.models import Campaign, Message, Receipt
from dm.api import senddm
from celery.utils.log import get_task_logger
from moderation.social import followersids
import logging
import random
import time
import datetime

logger = logging.getLogger(__name__)
celery_logger = get_task_logger(__name__)

def hoursago(hours):
    delta = datetime.timedelta(hours=hours)
    return datetime.datetime.now() - delta

def randinterval():
    return random.randint(300, 600)/10.0

def _format(message, socialuser, campaign):
    d = {
        'screen_name' : socialuser.profile.screen_name_tag(),
    }
    return message.content.format(**d)

@app.task
def handle_campaign(name):
    celery_logger.debug("Task launched for campaign %s", name)
    logger.debug("Task launched for campaign %s", name)
    try:
        campaign = Campaign.objects.get(name=name)
    except Campaign.DoesNotExist:
        return

    messages = campaign.messages.all()
    categories = campaign.categories.all()
    bot_su = SocialUser.objects.get(user_id=settings.BOT_ID)
    followersids(bot_su)
    bot_followers = Follower.objects.filter(user=bot_su).latest().followers

    receipts = Receipt.objects.filter(created__gte=hoursago(24))
    limit = settings.MESSENGER_DM_LIMIT
    #current_limit = limit - receipts.count()
    current_limit = limit


    socialuser_lst = []
    for category in categories:
        cat_lst = category.socialuser_set.filter(user_id__in=bot_followers)
        socialuser_lst.extend(list(cat_lst)) 
    
    logger.debug("socialuser_lst %s", socialuser_lst)

    campaign.recipients.set(socialuser_lst)
    campaign.save()
    
    for recipient in campaign.recipients.all():
        for msg in messages:
            receipts = Receipt.objects.filter(
                campaign = campaign,
                message = msg,
                user = recipient
            )
            skip = False
            if receipts:
                for r in receipts:
                    receipt_info = (f"Tried sending this on {localize(r.created)} "
                                    f"Error: {r.error} ID: {r.event_id}")
                    logger.info(receipt_info)
                    celery_logger.info(receipt_info)
                    code = None
                    if r.error:
                        try:
                            code = r.error["errors"][0]["code"]
                        except:
                            pass
                    if r.event_id or code in [420,429,88]:
                        skip = True

            if skip:
                logger.info("SKIPPING!")
                continue

            text=_format(msg, recipient, campaign)

            time.sleep(randinterval())

            if current_limit>0:
                response = senddm(
                    text,
                    user_id=recipient.user_id
                )
            else:
                response = f"No remaining DM (limit={current_limit})"
            
            current_limit-=1

            r = Receipt(campaign= campaign, message=msg, user=recipient)
            
            try:
                code = response["errors"][0]["code"]
            except:
                code = None

            if code in [420,429,88]:
                current_limit=0
            
            try:
                eventid = int(response["event"]["id"])
                r.event_id = eventid
                r.save()
            except:
                r.error = response
                r.save()