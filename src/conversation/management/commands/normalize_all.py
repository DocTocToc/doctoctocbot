from django.core.management.base import BaseCommand, CommandError

from conversation.tasks import handle_allnormalize


class Command(BaseCommand):
    help = 'Normalize data: set relevant hashtag, quoted & retweeted boolean columns from json'
    
    def handle(self, *args, **options):
        handle_allnormalize.apply_async()
        self.stdout.write(self.style.SUCCESS('Launched celery task to normalize status database.'))