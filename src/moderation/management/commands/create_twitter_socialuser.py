""" Create a Twitter SocialUser object from userid or screen_name """

import logging
from django.core.management.base import BaseCommand, CommandError
from moderation.profile import create_twitter_social_user_and_profile
from bot.tweepy_api import get_api
from tweepy.error import TweepError

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create SocialUser object from userid or screen name'
    
    def add_arguments(self, parser):
        parser.add_argument('user', type=str)
    
    def handle(self, *args, **options):
        user =  options['user']
        if not user:
            self.stdout.write(self.style.ERROR('You must provide a username or a userid.'))
            return
        userid = None
        screen_name = None
        try:
            userid=int(user)
        except ValueError:
            screen_name = user
        if screen_name:
            try:
                tweepy_user = get_api().get_user(screen_name=screen_name)
            except TweepError as e:
                raise CommandError('Tweepy error "%s' % e)
            except AttributeError as e:
                logger.error(f"AttributeError: {e}")
                return
            userid=tweepy_user.id
            self.stdout.write(f"user id: {userid}")
        su, created = create_twitter_social_user_and_profile(userid)
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Done creating SocialUser object {su}.'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'SocialUser object {su} already exists.'
                )
            )