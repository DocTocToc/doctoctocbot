from django.core.management.base import BaseCommand, CommandError

from moderation.lists.poll import poll


class Command(BaseCommand):
    help = 'Get json user (profile) object of given Twitter id or username'
    
    def add_arguments(self, parser):
        parser.add_argument('poll_id', nargs='+', type=int)
        
    def handle(self, *args, **options):
        poll()
        self.stdout.write(self.style.SUCCESS('Done retrieving profile.'))