""" Link Mastodon and Twitter users """

import logging
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from fediverse.models import MastodonInvitation
from django.db import  DatabaseError
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
        parser.add_argument(
            "-suid",
            "--socialuserid",
            type=int,
            help="SocialUser id"
        )

    def handle(self, *args, **options):
        suid: int = options['socialuserid']
        acct: str =  options['mastodon']
        twitter_username: str =  options['twitter']
        twitter_username = twitter_username.lower()
        if acct.find('@') == 0:
            acct = acct[1:]
        if '@' not in acct:
            if settings.MASTODON_DOMAIN:
                acct+=f'@{settings.MASTODON_DOMAIN}'
        if suid:
            try:
                su = SocialUser.objects.get(user_id=suid)
            except SocialUser.DoesNotExist:
                raise CommandError(
                'SocialUser with user_id "%s" does not exist' % suid
            )
        else:
            try:
                su = SocialUser.objects.get(
                    profile__json__screen_name__iexact=twitter_username
                )
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
            self.stdout.write(
                self.style.WARNING(
                    'MastodonUser with acct "%s" does not exist' % acct
                )
            )
            answer = input(
                f'Do you want to create MastodonUser "{acct}" ? (Y or N)'
            )
            if answer in ["Y", "y", "Yes", "yes"]:
                try:
                    mu=MastodonUser.objects.create(acct=acct)
                except DatabaseError as e:
                    raise CommandError(
                        f'Database error during new MastodonUser creation: {e}'
                    )
            else:
                raise CommandError(
                    f'Deal with it!'
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
                    self.style.SUCCESS(
                        f'{mu} and {su} are now linked by the same entity {su.entity}'
                    )
                )
            return
        elif su.entity:
            mu.entity=su.entity
            mu.save()
            self.stdout.write(
                    self.style.SUCCESS(
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
                self.style.SUCCESS(
                    f'{mu} and {su} are now linked by the same entity {mu.entity}'
                )
            )