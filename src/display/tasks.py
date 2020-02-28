import logging
from celery import shared_task
from .constants import HOURS
from conversation.tree.tweet_server import get_tweet
from .models import create_or_update_webtweet
from timeline.models import last_retweeted_statusid_lst
from community.models import Community

logger = logging.getLogger(__name__)

@shared_task
def handle_scrape_web_timeline(hourdelta=None):
    for community in Community.objects.filter(active=True):
        if hourdelta is None:
            hourdelta = HOURS    
        for sid in last_retweeted_statusid_lst(hourdelta, community):
            tweet = get_tweet(sid)
            if tweet is None:
                continue
            create_or_update_webtweet(tweet)
            
@shared_task
def handle_scrape_status(statusid: int):
            tweet = get_tweet(statusid)
            logger.debug(tweet)
            if tweet is None:
                return
            create_or_update_webtweet(tweet)