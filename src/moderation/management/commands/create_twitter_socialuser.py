""" Create a Twitter SocialUser object from userid or screen_name """

import logging
from django.core.management.base import BaseCommand, CommandError
from moderation.profile import create_twitter_social_user_and_profile
from moderation.models import SocialUser
from bot.tweepy_api import get_api
from tweepy.error import TweepError
from typing import List

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create SocialUser object from userids or screen names'
    
    def add_arguments(self, parser):
        parser.add_argument('users', nargs='+', type=str)
    
    def handle(self, *args, **options):
        users: List =  options['users']
        if not users:
            self.stdout.write(
                self.style.ERROR(
                    'You must provide one or more username(s) or userid(s).'
                )
            )
            return
        for user in users:
            user_id = None
            screen_name = None
            try:
                user_id=int(user)
                if SocialUser.objects.filter(user_id=user_id).exists():
                    self.stdout.write(
                        self.style.ERROR(
                            f'SocialUser object with user id {user_id} '
                            'already exists.'
                        )
                    )
                    continue
            except ValueError:
                screen_name = user
            if screen_name:
                api = get_api()
                if not api:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Could not get functional API.'
                        )
                    )
                    return
                try:
                    tweepy_user = get_api().get_user(screen_name=screen_name)
                except TweepError as e:
                    raise CommandError('Tweepy error "%s' % e)
                except AttributeError as e:
                    logger.error(f"AttributeError: {e}")
                    return
                user_id=tweepy_user.id
                self.stdout.write(f"user id: {user_id}")
            su, created = create_twitter_social_user_and_profile(user_id)
            if created and su:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Done creating SocialUser object {su}.'
                    )
                )
            elif su:
                self.stdout.write(
                    self.style.ERROR(
                        f'SocialUser object {su} already exists.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error, no new user was created.'
                    )
                )