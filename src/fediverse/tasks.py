import logging
from celery import shared_task
from community.models import Community
from fediverse.bot import TootProcessor

logger = logging.getLogger(__name__)

@shared_task
def handle_triage_toot(pk: int, community: str):
    try:
        community = Community.objects.get(name=community)
    except Community.DoesNotExist:
        return
    tp=TootProcessor(pk, community)
    res = tp.triage()
    logger.debug(res)