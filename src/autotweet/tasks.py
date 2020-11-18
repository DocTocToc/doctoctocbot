from __future__ import absolute_import, unicode_literals

from celery import shared_task

import logging
from autotweet.tree import get_all_replies
from community.models import Community

logger = logging.getLogger(__name__)


@shared_task(time_limit=86400)
def handle_get_all_replies(community_name: str):
    try:
        community = Community.objects.get(name=community_name)
    except Community.DoesNotExist:
        return
    get_all_replies(community)