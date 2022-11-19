""" Link Mastodon and Twitter users """

import logging
from django.core.management.base import BaseCommand, CommandError
from mastodon.models import MastodonInvitation
from moderation.models import MastodonUser, SocialUser, Entity
from typing import List
from moderation.social import get_socialuser_from_screen_name

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Link Mastodon and Twitter users'
    count = 0

    def add_arguments(self, parser):
        parser.add_argument(
            "-m",
            "--mastodon",
            type=str,
            help="Mastodon acct"
        )
        parser.add_argument(
            "-t",
            "--twitter",
            type=str,
            help="Twitter username"
        )

    def handle(self, *args, **options):
        acct: str =  options['mastodon']
        twitter_username: str =  options['twitter']
        try:
            su = SocialUser.objects.get(profile__json__screen_name=twitter_username)
        except SocialUser.DoesNotExist:
            raise CommandError(
                'Twitter SocialUser with username "%s" does not exist' % twitter_username
            )
        except SocialUser.MultipleObjectsReturned:
            raise CommandError(
                'More than one Twitter SocialUser with username "%s"' % twitter_username
            )
        try:
            mu=MastodonUser.objects.get(acct=acct)
        except MastodonUser.DoesNotExist:
            raise CommandError(
                'MastodonUser with acct "%s" does not exist' % acct
            )
        if mu.entity and su.entity:
            if mu.entity == su.entity:
                self.stdout.write(
                    self.style.WARNING(
                        f'{mu} and {su} are already linked by the same entity {mu.entity}'
                    )
                )
                return
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'{mu} entity: {mu.entity}\n'
                        f'{su} entity: {su.entity}\n'
                        'Please fix manually.'
                    )
                )
                return
        elif mu.entity:
            su.entity=mu.entity
            su.save()
            self.stdout.write(
                    self.style.WARNING(
                        f'{mu} and {su} are now linked by the same entity {su.entity}'
                    )
                )
            return
        elif su.entity:
            mu.entity=su.entity
            mu.save()
            self.stdout.write(
                    self.style.WARNING(
                        f'{mu} and {su} are now linked by the same entity {mu.entity}'
                    )
                )
            return
        else:
            try:
                entity = Entity.objects.create()
            except:
                raise CommandError(
                'Database error during new Entity creation'
            )
            su.entity=entity
            su.save()
            mu.entity=entity
            mu.save()
            self.stdout.write(
                self.style.WARNING(
                    f'{mu} and {su} are now linked by the same entity {mu.entity}'
                )
            )