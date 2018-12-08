import requests

from .tweet_parser import Tweet, TweetContext, TweetParser

"""
Interfaces with Twitter API server.
"""
    
def request_tweets(tweet: Tweet) -> TweetContext:
    url = get_url_for_tweet(tweet)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5"}
    page = requests.get(url=url, headers=headers, timeout=3)
    raw_html = page.content
    return TweetParser.parse_tweets_from_html(raw_html)

def request_continuation(tweet, continuation) -> TweetContext:
        url = get_url_for_conversation(tweet, continuation);
        response = async_get(url);
        return TweetParser.parse_tweets_from_conversation_html(response)

def async_get(url: str) -> str:
        return
    
def get_url_for_tweet(tweet: Tweet) -> str:
        return f'https://twitter.com/{tweet.username}/status/{tweet.id}'
    
def get_url_for_conversation(tweet: Tweet, continuation: str) -> str:
        return f'https://twitter.com/i/{tweet.username}/conversation/{tweet.id}?max_position=${continuation}'