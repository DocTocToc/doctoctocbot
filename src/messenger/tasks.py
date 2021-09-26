import logging
from constance import config
from celery import shared_task
from messenger.models import Campaign
from celery.utils.log import get_task_logger
from messenger.campaign import CampaignManager

logger = logging.getLogger(__name__)
celery_logger = get_task_logger(__name__)

# time limit set in constance database table
@shared_task(time_limit=config.messenger__tasks__handle_campaign__time_limit)
def handle_campaign(name):
    celery_logger.debug("Task launched for campaign %s", name)
    try:
        campaign = Campaign.objects.get(name=name)
    except Campaign.DoesNotExist:
        return
    #run_campaign(campaign)
    logger.debug(f'{campaign=}')
    cm = CampaignManager(campaign)
    logger.debug(f'{cm=}')
    cm.start()

