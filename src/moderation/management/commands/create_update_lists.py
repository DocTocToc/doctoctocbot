from django.core.management.base import BaseCommand, CommandError

from moderation.lists.poll import create_update_lists


class Command(BaseCommand):
    help = 'Create or update instances of TwitterList table with lists of authenticated Twitter account'
    
    def handle(self, *args, **options):
        create_update_lists()
        self.stdout.write(self.style.SUCCESS('Done creating / updating lists.'))