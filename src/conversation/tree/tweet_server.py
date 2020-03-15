import logging
from requests.exceptions import RequestException
from common.soup import raw_html
from common.twitter import status_url_from_id

from .tweet_parser import Tweet, TweetContext, parse_tweets_from_conversation_html, parse_tweets_from_html

logger = logging.getLogger(__name__)

"""
Interfaces with Twitter API server.
"""

def request_tweets(tweet: Tweet) -> TweetContext:
    url = get_url_for_tweet(tweet)
    raw = raw_html(url)
    if raw is None:
        return
    return parse_tweets_from_html(raw)

def request_context(statusid: int, screen_name: str = None) -> TweetContext:
    return request_tweets(Tweet(statusid=statusid, screen_name=screen_name))

def request_continuation(tweet, continuation) -> TweetContext:
        url = get_url_for_conversation(tweet, continuation);
        raw_html = raw_html(url)
        return parse_tweets_from_conversation_html(raw_html)
    
def get_url_for_tweet(tweet: Tweet) -> str:
        if tweet.screen_name:
            return f'https://twitter.com/{tweet.screen_name}/status/{tweet.statusid}'
        else:
            return status_url_from_id(tweet.statusid)
    
def get_url_for_conversation(tweet: Tweet, continuation: str) -> str:
        return f'https://twitter.com/i/{tweet.screen_name}/conversation/{tweet.statusid}?max_position=${continuation}'
    
def get_tweet(statusid: int) -> Tweet:
    tweet = Tweet(statusid)
    tweet_context = request_tweets(tweet)
    if tweet_context is None:
        return
    tweet = tweet_context.tweet
    if tweet_context.in_reply_to_status_id is not None:
        tweet.in_reply_to_status_id = tweet_context.in_reply_to_status_id
    return tweet