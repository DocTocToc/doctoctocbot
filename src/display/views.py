import time
from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

from conversation.tree.tweet_server import get_tweet
from .models import WebTweet, createwebtweet

import logging
logger = logging.getLogger(__name__)


# Create your views here.
def status(request, statusid):
    if not WebTweet.objects.filter(pk=statusid).exists():        
        tweet = get_tweet(statusid)
        if tweet is None:
            html = "<html><body>There is no tweet with id %s.</body></html>" % statusid
            return HttpResponse(html)
        createwebtweet(tweet)
    
    tweet = WebTweet.objects.get(pk=statusid)
    logger.debug(f"{tweet.localtime()}")
    logger.debug(f"{tweet.html}")
    localdatetime: str = time.strftime('%H:%M - %d %b %Y', tweet.localtime())
    utcdatetime: str = time.strftime('%d %B %Y %H:%M:%S', tweet.utctime())
    logger.debug(f"retweets: {tweet.retweet}")
    logger.debug(f"{localdatetime}")
    html = addurl(tweet.html, "https://twitter.com")
    context = {'tweet': tweet,
               'bodyhtml': mark_safe(html),
               'avatar_mini': mark_safe(tweet.avatar_mini),
               'localdatetime': localdatetime,
               'utcdatetime': utcdatetime}
    return render(request, 'display/tweet.html', context)

def addurl(fragment: str, url: str) -> str:
    logger.debug(f"fragment:{fragment}")
    def rawsoup(soup):
        if soup.body:
            return soup.body.next
        elif soup.html:
            return soup.html.next
        else:
            return soup

    soup = BeautifulSoup(fragment, 'lxml')
    logger.debug(f"soup before:{soup}")

    for a in soup.findAll('a'):
        if a['href'].startswith('/'):
            a['href'] = url + a['href']
    logger.debug(f"soup after:{soup}")
    soup = rawsoup(soup)
    logger.debug(f"rawsoup:{soup}")
    return str(soup)