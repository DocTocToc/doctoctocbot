import logging
from celery import shared_task
from community.models import Community
from fediverse.social import record_friends, record_followers
from fediverse.utils import triage, warn

logger = logging.getLogger(__name__)

@shared_task
def handle_warn_toot(pk: int, community: str):
    warn(pk, community)

@shared_task
def handle_triage_toot(pk: int, community: str):
    triage(pk, community)

@shared_task
def handle_mastodon_all_communities_friends():
    for c in Community.objects.filter(
        mastodon_account__isnull=False,
        mastodon_access__isnull=False,
        active=True,
    ):
        record_friends(c.mastodon_account, c.mastodon_access)

@shared_task
def handle_mastodon_all_communities_followers():
    for c in Community.objects.filter(
        mastodon_account__isnull=False,
        mastodon_access__isnull=False,
        active=True,
    ):
        record_followers(c.mastodon_account, c.mastodon_access)