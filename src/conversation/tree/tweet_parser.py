from typing import List
import time
#from lxml.html import HtmlElement
from bs4 import BeautifulSoup
from common.soup import doc_from_raw_html
import logging
logger = logging.getLogger(__name__)

class Tree:
    pass

class Tweet:
    """
    Contains information about an individual tweet.
    """
    def __init__(self,
                statusid = 0,
                conversationid = 0,
                in_reply_to_status_id: int = None,
                userid = 0,
                screen_name = "",
                name = "",
                bodyhtml = "",
                bodytext = "",
                avatar_mini = "",
                avatar_normal = "",
                avatar_bigger = "",
                time = 0,
                replies = 0,
                favorites = 0,
                retweets = 0,
                rtl = False,
                images: List[str] = None):
        if images is None:
            images = []
        self.images = images
        # Unique identifier of the tweet.
        self.statusid = statusid
        # Unique identifier of the conversation this tweet belongs to, corresponds to the statusid of the first status in the thread.
        self.conversationid = conversationid
        
        self.in_reply_to_status_id: int = in_reply_to_status_id
        
        # user_id (int)
        self.userid = userid
        # Handle of user who posted tweet.
        self.screen_name = screen_name
        # Screen name of user who posted tweet.
        self.name = name
        # HTML body of the tweet content.
        self.bodyhtml = bodyhtml
        self.bodytext = bodytext
        # URL of the avatar image for the user who posted the tweet.
        self.avatar_mini = avatar_mini
        self.avatar_bigger = avatar_bigger
        self.avatar_normal = avatar_normal
        # Time of the tweet in seconds since epoch.
        self.time = time
        # Number of replies (public and private) to the tweet.
        self.replies = replies
        # number of times this tweet was retweeted
        self.retweets = retweets
        # number of times this tweet was liked
        self.favorites = favorites
        # Whether to render the tweet as right-to-left.
        self.rtl = rtl

        self.images = images

    def get_url(self) -> str:
        """
        Returns a URL to this tweet on Twitter.
        """
        return f'https://twitter.com/{self.screen_name}/status/{self.id}'

    def get_user_url(self) -> str:
        """
        Returns a URL to the profile that posted this tweet on Twitter.
        """
        return f'https://twitter.com/{self.screen_name}'
    
    def setcount(self, tweet_element: BeautifulSoup):
        
        if self.statusid == 0:
            return
        
        def textcount(txt: str) -> int:
            try:
                val_int = int(txt.split()[0])
            except IndexError:
                val_int = 0
            return val_int
        """
        #fav
        span1 = tweet_element.find('span', attrs={'class'='ProfileTweet-action--favorite'}
        span2 = tweet_element.find('span', attrs={'class'='data-tweet-stat-count'}
        self.favorites = span2['data-tweet-stat-count']
        
        #rt
        span1 = tweet_element.find('span', attrs={'class'='ProfileTweet-action--retweet'}
        span2 = tweet_element.find('span', attrs={'class'='data-tweet-stat-count'}
        self.retweets = span2['data-tweet-stat-count']                      
        """
        _dict = {"reply": "replies", "retweet": "retweets", "favorite": "favorites"}
        for k in _dict.keys():
            spanid = f"profile-tweet-action-{k}-count-aria-{self.statusid}"
            element = tweet_element.find('span', attrs={'id': spanid})
            parent = element.parent
            count_str = parent['data-tweet-stat-count']
            count_int = int(count_str)
            setattr(self, _dict[k], count_int)
            
    def localtime(self):
        """
        Converts the epoch in seconds from a Tweet object to a Python localtime object
        """
        return time.localtime(self.time)
    
    def utctime(self):
        return time.gmtime(self.time)

class TweetContext:
    """
    Represents the context of a conversation around a particular tweet. this
    consists of the tweet itself, (some of) the tweets before it in its
    reply-chain, and (some of) the reply chains that come after it.
    """
    def __init__(self,
                 ancestors: List[Tweet] = None,
                 tweet: Tweet = None,
                 in_reply_to_status_id = None,
                 descendants: List[List[Tweet]] = None,
                 continuation: str = ""):
        # Tweets before this.tweet in the reply-chain.
        if ancestors is None:
            ancestors = []
        self.ancestors = ancestors
    
        # The tweet that this TweetContext relates to.
        if tweet is None:
            tweet = Tweet()
        self.tweet = tweet
         
        #The ID of an existing status that the update is in reply to.
        self.in_reply_to_status_id = in_reply_to_status_id 
        
        # Chains of replies in response to this.tweet.
        if descendants is None:
            descendants = []
        self.descendants = descendants
    
        # If present, an API token used to loading more descendants.
        #If absent, indicates no further replies.
        self.continuation = continuation


"""
Functions for parsing a response from the twitter API into Tweet and
TweetContext objects.
"""
    

def parse_tweets_from_conversation_html(raw_html: bytes) -> TweetContext:
    """
    Given an API response with a conversation continuation, parse and return the TweetContext.
    """
    soup = doc_from_raw_html(raw_html)

    context = TweetContext();
    context.descendants = parse_descendants(soup.find('body'))
    # context.continuation = obj.min_position
    return context

def parse_tweets_from_html(raw_html: bytes) -> TweetContext:
    """
    Given an API response about a particular tweet, parse and return the 
    TweetContext.
    """
    soup = doc_from_raw_html(raw_html)
    if not soup:
        return
    
    tweet_context = TweetContext()
    
    try:
        show_more_threads_button = soup.find_all(attrs={'class':'ThreadedConversation-showMoreThreadsButton'})[0]
    except IndexError:
        show_more_threads_button = None
    
    if show_more_threads_button:
        tweet_context.continuation = show_more_threads_button['data-cursor']
    else:
        try:
            div_data_min_position = soup.find("div", class_="replies-to").find("div", class_="stream-container")
        except AttributeError:
            div_data_min_position = None
            
        if div_data_min_position:
            tweet_context.continuation = div_data_min_position['data-min-position']

    try:
        ancestor_container = soup.find_all(attrs={'class':'in-reply-to'})[0]
    except IndexError:
        ancestor_container = None
        
    try:
        main_tweet_container = soup.find_all(attrs={'class':'permalink-tweet-container'})[0]
    except IndexError:
        main_tweet_container = None
    
    try:
        descendants_container = soup.find_all(attrs={'class':'replies-to'})[0]
    except IndexError:
        descendants_container = None

    if ancestor_container:
        def has_attr_replied(tag):
            return tag.has_attr('data-replied-tweet-id')
        
        try:
            #tweet_context.in_reply_to_status_id = ancestor_container.find_all(has_attr_replied)[0].get('data-replied-tweet-id')
            tweet_context.in_reply_to_status_id = ancestor_container.get('data-replied-tweet-id')
        except IndexError:
            pass
        
        tweet_context.ancestors = parse_tweets_from_stream(ancestor_container)

    if main_tweet_container:
        try:
            tweet_context.tweet = parse_tweets_from_stream(main_tweet_container)[0]
        except IndexError:
            pass

    if descendants_container:
        tweet_context.descendants = parse_descendants(descendants_container)
    
    return tweet_context

def parse_descendants(soup: BeautifulSoup) -> List[List[Tweet]]:
    descendants = soup.find_all('li', attrs={'class':['ThreadedConversation', 'ThreadedConversation--loneTweet']})
    result: List[List[Tweet]] = []

    for child in descendants:
        result.append(parse_tweets_from_stream(child))
    return result

def parse_tweets_from_stream(soup: BeautifulSoup) -> List[Tweet]:
    tweetStream = []
    tweetElements = soup.find_all("div", class_="tweet")

    for tweetElement in tweetElements:
        tweet = Tweet()
        
        tweet.userid = int(tweetElement['data-user-id'])
        
        tweet.screen_name = tweetElement['data-screen-name']
        
        tweet.name = tweetElement.find_all(attrs={'class':'fullname'})[0].text
        
        tweet.bodytext = tweetElement.find_all(attrs={'class':'tweet-text'})[0].text
        
        tweet.rtl = bool(len(tweetElement.find_all(attrs={'class':'tweet-text-rtl'})))
        
        tweet.bodyhtml = tweetElement.find_all(attrs={'class':'tweet-text'})[0].decode_contents()
        
        tweet.statusid = tweetElement['data-tweet-id']
        
        tweet.conversationid = int(tweetElement['data-conversation-id'])
        
        avatar_bigger = tweetElement.find_all(attrs={'class':'avatar'})[0]['src']
        tweet.avatar_bigger = avatar_bigger
        tweet.avatar_mini = avatar_bigger.replace('_bigger', '_mini')
        tweet.avatar_normal = avatar_bigger.replace('_bigger', '_normal')
        
        tweet.time = int(tweetElement.find_all(attrs={'class':'_timestamp'})[0]['data-time'])
        """
        try:
            replies_str = tweetElement.find_all('button', attrs={'class':'js-actionReply'})[0].find_all('span', attrs={'class':'ProfileTweet-actionCountForPresentation'})[0].text
        except IndexError:
            replies_str = None
            
        try:
            replies_int = int(replies_str)
        except ValueError:
            replies_int = 0
        tweet.replies = replies_int
        """
        tweet.setcount(tweetElement)
        
        for div in tweetElement.find_all('div', attrs={'AdaptiveMedia-photoContainer'}):
                tweet.images.append(div.find('img')['src'])

        tweetStream.append(tweet)
    return tweetStream

