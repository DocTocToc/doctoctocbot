from django.core.management.base import BaseCommand, CommandError

from conversation.tasks import update_retweet


class Command(BaseCommand):
    help = 'For all Accounts, check for unretweets'
    
    def add_arguments(self, parser):
        parser.add_argument('days', type=int)
    
    def handle(self, *args, **options):
        days = options['days']
        update_retweet.apply_async(args=(days,), ignore_result=True)
        self.stdout.write(self.style.SUCCESS('Launched celery task to update retweets.'))