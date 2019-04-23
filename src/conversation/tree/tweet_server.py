import logging
from requests import get
from requests.exceptions import RequestException
from contextlib import closing

from .tweet_parser import Tweet, TweetContext, parse_tweets_from_conversation_html, parse_tweets_from_html

logger = logging.getLogger(__name__)

"""
Interfaces with Twitter API server.
"""

def request_url(url: str):
    #headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    #    "Accept-Language": "en-US,en;q=0.5"}
    return simple_get(url)
    
def request_tweets(tweet: Tweet) -> TweetContext:
    url = get_url_for_tweet(tweet)
    raw_html = request_url(url)
    if raw_html is None:
        return
    return parse_tweets_from_html(raw_html)

def request_context(statusid: int, username: str = None) -> TweetContext:
    return request_tweets(Tweet(statusid=statusid, username=username))

def request_continuation(tweet, continuation) -> TweetContext:
        url = get_url_for_conversation(tweet, continuation);
        raw_html = request_url(url)
        return parse_tweets_from_conversation_html(raw_html)
    
def get_url_for_tweet(tweet: Tweet) -> str:
        if tweet.username:
            return f'https://twitter.com/{tweet.username}/status/{tweet.statusid}'
        else:
            return f'https://twitter.com/statuses/{tweet.statusid}'
    
def get_url_for_conversation(tweet: Tweet, continuation: str) -> str:
        return f'https://twitter.com/i/{tweet.username}/conversation/{tweet.statusid}?max_position=${continuation}'
    
def get_tweet(statusid: int) -> Tweet:
    tweet = Tweet(statusid)
    tweet_context = request_tweets(tweet)
    if tweet_context is None:
        return
    tweet = tweet_context.tweet
    if tweet_context.in_reply_to_status_id is not None:
        tweet.in_reply_to_status_id = tweet_context.in_reply_to_status_id
    return tweet

def simple_get(url):
    """
    ...
    """
    def is_good_response(resp):
        content_type = resp.headers['Content-Type'].lower()
        return(resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)
    
    def log_error(e):
        print(e)
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.5"}
    try:
        with closing(get(url, headers=headers, timeout=3, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None