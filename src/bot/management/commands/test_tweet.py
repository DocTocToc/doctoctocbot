from django.core.management.base import BaseCommand, CommandError

from bot.tests.tweet import main


class Command(BaseCommand):
    help = 'Test the bot'
    
    def add_arguments(self, parser):
        parser.add_argument('hashtag', type=str)
    
    def handle(self, *args, **options):
        hashtag = options['hashtag']
        main(hashtag)
        self.stdout.write(self.style.SUCCESS('Done testing tweet.'))