""" Create a Twitter SocialUser object from userid or screen_name """

from django.core.management.base import BaseCommand, CommandError

from moderation.models import SocialUser, SocialMedia
from bot.twitter import get_api
from tweepy.error import TweepError

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
            userid=tweepy_user.id
            self.stdout.write(f"user id: {userid}")
        try:
            twitter = SocialMedia.objects.get(name='twitter')
        except SocialMedia.DoesNotExist:
            self.stdout.write(self.style.ERROR('Twitter SocialMedia object does not exist.'))
            return
        _su, created = SocialUser.objects.get_or_create(user_id=userid, social_media=twitter)
        if created:
            self.stdout.write(self.style.SUCCESS('Done creating SocialUser object.'))
        else:
            self.stdout.write(self.style.ERROR('SocialUser object already exists.'))