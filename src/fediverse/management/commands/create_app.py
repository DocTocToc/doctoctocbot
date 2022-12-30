""" Create Mastodon app """

import logging
from django.core.management.base import BaseCommand, CommandError
from moderation.profile import create_twitter_social_user_and_profile
from fediverse.models import MastodonApp, MastodonScopes
from mastodon import Mastodon, MastodonError
from django.db import DatabaseError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Create a new Mastodon app with given `client_name` and `scopes` (The basic scopes are "read", "write", "follow" and "push"
    - more granular scopes are available, please refer to Mastodon documentation for which) on the instance given
    by `api_base_url`"""

    def add_arguments(self, parser):
        parser.add_argument(
            'client_name',
            type=str,
            help="name of the app")
        parser.add_argument(
            "-s",
            "--scopes",
            action="extend",
            nargs="+",
            type=str
        )
        parser.add_argument(
            "-r",
            "--redirect_uris",
            action="extend",
            nargs="+",
            type=str,
            help=(
                "Specify `redirect_uris` if you want users to be redirected to" "a certain page after authenticating in an OAuth flow."
                "You can specify multiple URLs by passing a list. Note that if" "you wish to use OAuth authentication with redirects,"
                "the redirect URI must be one of the URLs specified here."
            )
        )
        parser.add_argument(
            "-a",
            "--api_base_url",
            type=str,
            help="autofollow acct"
        )
        parser.add_argument(
            "-w",
            "--website",
            type=str,
            help="to give a website for your app"
        )

    def handle(self, *args, **options):
        self.client_name = options['client_name']
        logger.debug(f'{self.client_name=}')
        if MastodonApp.objects.filter(client_name=self.client_name).exists():
            raise CommandError(
                'An app with client_name "%s" already exists' % self.client_name
            )
        self.scopes = options['scopes']
        logger.debug(f'{self.scopes=}')
        self.redirect_uris = options['redirect_uris']
        logger.debug(f'{self.redirect_uris=}')
        self.api_base_url = options['api_base_url']
        logger.debug(f'{self.api_base_url=}')
        self.website = options['website']
        logger.debug(f'{self.website=}')

        scopes: MastodonScopes = []
        if not self.scopes:
            self.scopes = ["read", "write", "push"]
        for s in self.scopes:
            try:
                scopes.append(MastodonScopes.objects.get(scope=s))
            except MastodonScopes.DoesNotExist:
                continue
        logger.debug(f'{scopes=}')
        try:
            self.client_id, self.client_secret = Mastodon.create_app(
                self.client_name,
                api_base_url = self.api_base_url
            )
        except MastodonError as e:
            self.stdout.write(
                self.style.ERROR('Mastodon error: "%s"' % e)
            )
            raise CommandError()
        try:
            app = MastodonApp.objects.create(
                client_name=self.client_name,
                client_id=self.client_id,
                client_secret=self.client_secret,
                api_base_url=self.api_base_url,
                redirect_uris=self.redirect_uris,
                website=self.website,
            )
            app.scopes.add(*scopes)
            self.stdout.write(
                self.style.SUCCESS(
                    'App %s successfully recorded: %s' % (self.client_name, app)
                )
            )
        except DatabaseError as e:
            raise CommandError(
                'Database error: %s' % e
            )
