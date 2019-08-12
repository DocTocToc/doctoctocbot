from celery import shared_task
from .constants import HOURS
from conversation.utils import last_authorized_statusid_lst
from conversation.tree.tweet_server import get_tweet
from .models import create_or_update_webtweet
from timeline.models import last_retweeted_statusid_lst


@shared_task
def handle_scrape_web_roots(hourdelta=None):
    """
    TODO: scrap this task 
    last_authorized_statusid_lst selects statuses that contain hashtag0 but some
    root tweets don't contain the hashtag, which can be further down in the
    thread
    """
    if hourdelta is None:
        hourdelta = HOURS    
    for sid in last_authorized_statusid_lst(hourdelta):
        tweet = get_tweet(sid)
        if tweet is None:
            continue
        create_or_update_webtweet(tweet)
        

@shared_task
def handle_scrape_web_timeline(hourdelta=None):
    if hourdelta is None:
        hourdelta = HOURS    
    for sid in last_retweeted_statusid_lst(hourdelta):
        tweet = get_tweet(sid)
        if tweet is None:
            continue
        create_or_update_webtweet(tweet)