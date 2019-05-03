""" Create missing SocialUser profiles. Get user objects from tweets if
available. If no tweet from the user is available, do a Twitter API lookup. """

from django.core.management.base import BaseCommand, CommandError

from moderation.tasks import handle_create_all_profiles as create_all_profiles


class Command(BaseCommand):
    help = 'Create missing SocialUser profiles'
    
    def handle(self, *args, **options):
        create_all_profiles()
        self.stdout.write(self.style.SUCCESS('Done creating missing SocialUser profiles'))