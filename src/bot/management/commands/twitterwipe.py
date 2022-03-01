import logging
from bot.bin.twitterwipe import TwitterWipe
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Delete tweets, retweets, favorites.'
    
    def add_arguments(self, parser):
        parser.add_argument(
            "screen_name",
            type=str,
            help="Twitter account's screen_name"
        )
        parser.add_argument(
            "-t",
            "--tweets",
            type=int,
            help="tweets created in the last 't' days will be preserved"
        )
        parser.add_argument(
            "-r",
            "--retweets",
            type=int,
            help="retweets created in the last 'r' days will be preserved"
        )
        parser.add_argument(
            "-f",
            "--favorites",
            type=int,
            help="favorites created in the last 'f' days will be preserved"
        )

    def handle(self, *args, **options):
        username: str =  options['screen_name']
        tweets: int = options['tweets'] or 0
        retweets: int = options['retweets'] or 0
        favorites = options['favorites'] or 0
        tw = TwitterWipe(
            username,
            tweets=tweets,
            retweets=retweets,
            favorites=favorites
        )
        tw.run()