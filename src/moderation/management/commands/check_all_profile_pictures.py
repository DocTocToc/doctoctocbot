"""
Recreate missing SocialUser profiles pictures. Get user objects from tweets if
available.
"""

from django.core.management.base import BaseCommand, CommandError

from moderation.tasks import handle_check_all_profile_pictures as check_all_profile_pictures

class Command(BaseCommand):
    help = 'Create missing SocialUser profiles'
    
    def handle(self, *args, **options):
        check_all_profile_pictures()
        self.stdout.write(self.style.SUCCESS('Done creating missing SocialUser profiles'))