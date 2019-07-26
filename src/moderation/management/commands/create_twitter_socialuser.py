""" Create a Twitter SocialUser object from userid. """

from django.core.management.base import BaseCommand, CommandError

from moderation.models import SocialUser, SocialMedia


class Command(BaseCommand):
    help = 'Create SocialUser object from userid'
    
    def add_arguments(self, parser):
        parser.add_argument('userid', type=int)
    
    def handle(self, *args, **options):
        userid =  options['userid']
        if not userid:
            self.stdout.write(self.style.ERROR('You must provide a userid.'))
            return
        try:
            twitter = SocialMedia.objects.get(name='twitter')
        except SocialMedia.DoesNotExist:
            self.stdout.write(self.style.ERROR('Twitter SocialMedia object does not exist.'))
            return
        su, created = SocialUser.objects.get_or_create(user_id=userid, social_media=twitter)
        if created:
            self.stdout.write(self.style.SUCCESS('Done creating SocialUser object.'))
        else:
            self.stdout.write(self.style.ERROR('SocialUser object already exists.'))