""" Create Mastodon access """

import logging
from django.core.management.base import BaseCommand, CommandError
from fediverse.models import MastodonApp, MastodonScopes, MastodonAccess
from moderation.models import MastodonUser
from mastodon import Mastodon, MastodonError
from django.db import DatabaseError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Create access token for an app"""

    def add_arguments(self, parser):
        parser.add_argument(
            'client_name',
            type=str,
            help="name of the app"
        )
        parser.add_argument(
            '-a',
            '--acct',
            type=str,
            help="webfinger acct in the form 'user@mastodon.social'"
        )
        parser.add_argument(
            '-u',
            '--username',
            type=str,
            help="The username is the email address used to log in into Mastodon."
        )
        parser.add_argument(
            '-p',
            '--password',
            type=str,
            help="password"
        )

    def handle(self, *args, **options):
        self.client_name = options['client_name']
        logger.debug(f'{self.client_name=}')
        try:
            app = MastodonApp.objects.get(client_name=self.client_name)
        except MastodonApp.DoesNotExist:
            raise CommandError(
                'An app with client_name "%s" does not exist' % self.client_name
            )
        self.acct = options['acct']
        try:
            user = MastodonUser.objects.get(acct=self.acct)
        except MastodonUser.DoesNotExist:
            raise CommandError(
                'MastodonUser with acct "%s" does not exist' % self.acct
            )
        self.username = options['username']
        self.password = options['password']
        
        mastodon = Mastodon(
            client_id = app.client_id,
            client_secret = app.client_secret, 
            api_base_url = app.api_base_url,
        )
        try:
            access_token = mastodon.log_in(
                username=self.username,
                password=self.password,
                scopes=[s.scope for s in app.scopes.all()]
            )
        except MastodonError as e:
            raise CommandError(
                'Mastodon error: %s' % e
            )
        try:
            access = MastodonAccess.objects.create(
                app=app,
                user=user,
                access_token=access_token
            )
            self.stdout.write(
                self.style.SUCCESS(
                    'MastodonAccess %s successfully recorded' % access
                )
            )
        except DatabaseError as e:
            raise CommandError(
                'Database error: %s' % e
            )
