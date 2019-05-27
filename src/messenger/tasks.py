from doctocnet.celery import app
from messenger.models import Campaign, Message, Receipt
from dm.api import senddm
from celery.utils.log import get_task_logger
import logging

logger = logging.getLogger(__name__)
celery_logger = get_task_logger(__name__)

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
    
    socialuser_lst = []
    for category in categories:
        socialuser_lst.extend(category.socialuser_set.all()) 
    
    print(socialuser_lst)

    campaign.recipients.set(socialuser_lst)
    campaign.save()
    
    for recipient in campaign.recipients.all():
        for msg in messages:
            receipts = Receipt.objects.filter(
                campaign = campaign,
                message = msg,
                user = recipient
            )
            if receipts:
                for r in receipts:
                    logger.info(f"Message already sent on {r.created}")
                continue
            text=_format(msg, recipient, campaign)
            response = senddm(
                msg.content,
                user_id=recipient.user_id
            )
            print(response)
            r = Receipt(campaign= campaign, message=msg, user=recipient)
            try:
                eventid = int(response["event"]["id"])
                r.event_id = eventid
                r.save()
            except:
                r.error = response
                r.save()