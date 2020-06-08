from django.core.management.base import BaseCommand, CommandError
from bot.tweepy_api import get_api
from conversation.models import Tweetdj
from bot.lib.statusdb import Addstatus
from tweepy import TweepError
import logging

logger = logging.getLogger(__name__)
    
def truncated_count():
    return Tweetdj.objects.filter(json__truncated=True).count()


class Command(BaseCommand):
    help = 'Detect truncated tweets, get the fully hydrated versions, replace them.'

    
    def handle(self, *args, **options):
        truncated_count_start = truncated_count()
        api = get_api()
        if not api:
            self.stdout.write(self.style.ERROR("Invalid Twitter API"))
            return
        ids = Tweetdj.objects.filter(json__truncated=True).values_list('statusid', flat=True)
        for i in range(0, len(ids), 100):
            try:
                tweets = api.statuses_lookup(
                    ids[i:i+100],
                    include_entities=True,
                    map_=True,
                    tweet_mode="extended"
                )
            except TweepError as e:
                logger.error(e)
                break
            for tweet in tweets:
                # test if Tweet still exists (deleted tweets json objects only have one key, the id)
                if len(tweet._json.keys())>1:
                    try:
                        old = Tweetdj.objects.get(statusid=tweet._json["id"])
                    except Tweetdj.DoesNotExist:
                        continue
                    old.delete()
                    addstatus = Addstatus(tweet._json)
                    addstatus.addtweetdj()
        
        truncated_count_stop = truncated_count()
        hydrated =  truncated_count_start - truncated_count_stop
        message = (
            f"{truncated_count_start} tweet(s) were truncated. "
            f"{hydrated} more tweet(s) are now hydrated. "
            f"{truncated_count_stop} tweet(s) are still truncated."
        )
        self.stdout.write(self.style.SUCCESS(message))