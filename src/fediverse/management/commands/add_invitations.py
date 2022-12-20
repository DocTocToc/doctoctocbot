""" Add Mastodon invitations """

import logging
from django.core.management.base import BaseCommand, CommandError
from moderation.profile import create_twitter_social_user_and_profile
from fediverse.models import MastodonInvitation
from moderation.models import MastodonUser
from bot.tweepy_api import get_api
from tweepy.error import TweepError
from bot.account import random_bot_username
from typing import List
from moderation.social import get_socialuser_from_screen_name

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Add Mastodon invitations uid'
    count = 0

    def add_arguments(self, parser):
        parser.add_argument('uid', nargs='+', type=str)
        parser.add_argument(
            "-a",
            "--autofollow",
            type=str,
            help="autofollow acct"
        )

    def record_invitation(self, uid, autofollow=None):
        try:
            invite = MastodonInvitation.objects.create(
                uid=uid,
                autofollow=autofollow
            )
            self.count+=1
            self.stdout.write(
                self.style.WARN(
                    f'{invite} created.'
                )
            )
        except:
            pass

    def handle(self, *args, **options):
        uids: List =  options['uid']
        autofollow: str =  options['autofollow']
        try:
            mastodon_user_autofollow=MastodonUser.objects.get(acct=autofollow)
        except MastodonUser.DoesNotExist:
            raise CommandError(
                'MastodonUser with acct "%s" does not exist' % autofollow
            )
        for uid in uids:
            self.record_invitation(uid, autofollow=mastodon_user_autofollow)
        self.stdout.write(
                self.style.WARNING(
                    f'{self.count} invitations were added to MastodonInvitation table.'
                )
            )