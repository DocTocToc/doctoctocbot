from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from bot.tests.tweet import main
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test retweeting by the bot'
    
    def add_arguments(self, parser):
        parser.add_argument('hashtag', type=str, nargs='*')
    
    def handle(self, *args, **options):
        opt = options['hashtag']
        hashtag_lst = []
        if not opt:
            hashtag_lst = settings.KEYWORD_RETWEET_LIST
        elif isinstance(opt, list):
            hashtag_lst.extend(opt)
        else:
            hashtag_lst.append(opt)

        for hashtag in hashtag_lst:
            main(hashtag)
        self.stdout.write(self.style.SUCCESS('Done testing retweet.'))