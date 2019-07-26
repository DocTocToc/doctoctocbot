import time

from .tweet_server import request_tweets
from .tweet_parser import Tweet

def datetime_from_epoch(tweet: Tweet):
    """
    Converts the epoch in seconds from a Tweet object to a Python datetime object
    """
    return time.localtime(tweet.time)

def display(statusid):
    tweet = Tweet(statusid=statusid)
    tweet_context = request_tweets(tweet)
    tweet = tweet_context.tweet
    
    def printer_tc(tweet_context):
        print(f"in_reply_to_status_id:{tweet_context.in_reply_to_status_id}")
        printer_t(tweet_context.tweet)
        for tweet_lst in tweet_context.descendants:
            for tweet in tweet_lst:
                printer_t(tweet)
        
    
    def printer_t(tweet):
        datetime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tweet.time))
        print(f"statusid: {tweet.statusid}\n"
        f"conversation id: {tweet.conversationid}\n"
        f"user_id: {tweet.userid}\n"
        f"screen_name: {tweet.screen_name}\n"
        f"name: {tweet.name}\n"
        f"text: {tweet.bodytext}\n"
        f"html: {tweet.bodyhtml}\n"
        f"rtl: {tweet.rtl}\n"
        f"avatar: {tweet.avatar}\n"
        f"time (seconds since epoch): {tweet.time}\n"
        f"date & time: {datetime_str}\n"
        f"replies: {tweet.replies}\n"
        f"retweets: {tweet.retweets}\n"
        f"likes: {tweet.favorites}\n")
        
    printer_tc(tweet_context)