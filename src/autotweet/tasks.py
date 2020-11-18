from __future__ import absolute_import, unicode_literals
import logging

from celery import shared_task

from constance import config

from autotweet.tree import get_all_replies
from community.models import Community

logger = logging.getLogger(__name__)

soft = config.autotweet__tasks__handle_get_all_replies__soft_time_limit
hard = config.autotweet__tasks__handle_get_all_replies__time_limit

@shared_task(time_limit=hard, soft_time_limit=soft)
def handle_get_all_replies(community_name: str):
    try:
        community = Community.objects.get(name=community_name)
    except Community.DoesNotExist:
        return
    get_all_replies(community)