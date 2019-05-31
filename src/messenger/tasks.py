from django.utils.formats import localize
from django.conf import settings
from doctocnet.celery import app
from moderation.models import SocialUser
from messenger.models import Campaign, Message, Receipt
from dm.api import senddm
from celery.utils.log import get_task_logger
from moderation.social import followersids
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
    bot_su = SocialUser.objects.get(user_id=settings.BOT_ID)
    followersids(bot_su)
    bot_followers = Follower.objects.filter(user=bot_su).latest().followers

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
            if receipts:
                for r in receipts:
                    logger.info("Message already sent on %s", localize(r.created))
                    celery_logger.info("Message already sent on %s", localize(r.created))
                continue
            text=_format(msg, recipient, campaign)
            response = senddm(
                text,
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