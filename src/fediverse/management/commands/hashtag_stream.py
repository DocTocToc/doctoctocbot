import logging
from mastodon import Mastodon, StreamListener
from django.core.management.base import BaseCommand, CommandError
from community.models import Community, Reblog
from fediverse.api import get_mastodon_api
from fediverse.statusdb import TootDb
from fediverse.tasks import handle_triage_toot

logger = logging.getLogger(__name__)

class HashtagListener(StreamListener):

    def on_update(self, status):
        msg = f"on_update:\n#{self.tag} from {self.community}\n{status}"
        logger.debug(msg)
        tdb = TootDb(status)
        toot = tdb.add()
        logger.debug(toot)
        handle_triage_toot.apply_async(
            args=(toot.pk, self.community,)
        )


class CommunityHashtagListener(HashtagListener):

    def __init__(self, community: str, tag: str, **kwds):
        self.community = community
        self.tag = tag
        super().__init__(**kwds)


class Command(BaseCommand):
    help = 'Run Mastodon bot hashtag stream'

    def add_arguments(self, parser):
        parser.add_argument(
            'tag',
            type=str
        )
        parser.add_argument(
            '-c',
            '--community',
            type=str
        )

    def handle(self, *args, **options):
        tag = options['tag']
        try:
            community_name = options['community']
        except KeyError:
            return
        try:
            community = Community.objects.get(name=community_name)
            logger.debug(community)
        except Community.DoesNotExist:
            return
        mastodon = get_mastodon_api(
            acct=community.mastodon_access.user.acct,
            client_name=community.mastodon_access.app.client_name
        )
        listener = CommunityHashtagListener(
            community=community.name,
            tag=tag
        )
        mastodon.stream_hashtag(
            tag,
            listener,
            local=False,
            run_async=False,
            timeout=300,
            reconnect_async=False,
            reconnect_async_wait_sec=5
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Done launching #{tag} {community} Mastodon hashtag stream.'
            )
        )