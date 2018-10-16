from django.core.management.base import  BaseCommand, CommandError
from moderation.lists.poll import poll

class Command(BaseCommand):
    help = 'Polls lists of Twiter account, update UserModerationRelationship table'
    
    def handle(self, *args, **options):
        poll()
        self.stdout.write(self.style.SUCCESS('Done polling lists.'))