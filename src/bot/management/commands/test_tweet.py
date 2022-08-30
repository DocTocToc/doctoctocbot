from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from bot.tests.tweet import main
from common.twitter import status_url_from_id
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test retweeting by the bot'
    
    def add_arguments(self, parser):
        parser.add_argument('hashtag', type=str, nargs='+')
    
    def handle(self, *args, **options):
        hashtag_lst = options['hashtag']
        logger.debug(f'{isinstance(hashtag_lst, list)=}')
        for hashtag in hashtag_lst:
            response = main(hashtag)
            msg = ""
            try:
                sid = response._json["id"]
                status_url = status_url_from_id(sid)
                msg = status_url + " " + f'{response._json["text"]}'
                self.stdout.write(self.style.SUCCESS(f'{msg}\n'))
            except:
                self.stdout.write(self.style.SUCCESS(f'{response}\n'))
                continue
        self.stdout.write(self.style.SUCCESS('Done testing retweet.'))