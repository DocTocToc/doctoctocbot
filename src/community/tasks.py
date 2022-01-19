import logging

from community.models import Community
from bot.bin.friendship import create_friendship_members

from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def handle_follow_member():
    communities = Community.objects.filter(
        active=True,
        twitter_follow_member=True
    )
    for community in communities:
        handle_follow_member_community.apply_async(
            args=(community.name,),
            ignore_result=True
        )

@shared_task
def handle_follow_member_community(community: str):
    try:
        community = Community.objects.get(name=community)
    except Community.DoesNotExist:
        return
    create_friendship_members(community)