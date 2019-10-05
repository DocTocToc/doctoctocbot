from celery import shared_task
from .constants import HOURS
from conversation.tree.tweet_server import get_tweet
from .models import create_or_update_webtweet
from timeline.models import last_retweeted_statusid_lst
from community.models import Community

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