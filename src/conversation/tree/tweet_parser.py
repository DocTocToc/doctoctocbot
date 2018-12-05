from typing import List
#from lxml.html import HtmlElement
from bs4 import BeautifulSoup


class Tree:
    pass

class Tweet:
    """
    Contains information about an individual tweet.
    """
    
    # Unique identifier of the tweet.
    id: str
    # Handle of user who posted tweet.
    username: str
    # Screen name of user who posted tweet.
    name: str
    # HTML body of the tweet content.
    bodyHtml: str
    bodyText: str
    # URL of the avatar image for the user who posted the tweet.
    avatar: str
    # Time of the tweet in seconds since epoch.
    time: int
    # Number of replies (public and private) to the tweet.
    replies: int
    # Whether to render the tweet as right-to-left.
    rtl: bool

    images: List[str] = []


    def get_url(self) -> str:
        """
        Returns a URL to this tweet on Twitter.
        """
        return f'https://twitter.com/{self.username}/status/{self.id}'

    def get_user_url(self) -> str:
        """
        Returns a URL to the profile that posted this tweet on Twitter.
        """
        return f'https://twitter.com/{self.username}'
    

class TweetContext:
    """
    Represents the context of a conversation around a particular tweet. this
    consists of the tweet itself, (some of) the tweets before it in its
    reply-chain, and (some of) the reply chains that come after it.
    """
    
    # Tweets before this.tweet in the reply-chain.
    ancestors: List[Tweet] = []
    
    # The tweet that this TweetContext relates to.
    tweet: Tweet
    
    # Chains of replies in response to this.tweet.
    descentants: List[List[Tweet]] = []
    
    # If present, an API token used to loading more descendants.
    #If absent, indicates no further replies.
    continuation: str


"""
Functions for parsing a response from the twitter API into Tweet and
TweetContext objects.
"""
    

def parse_tweets_from_conversation_html(response: str) -> TweetContext:
    """
    Given an API response with a conversation continuation, parse and return the TweetContext.
    """
    obj = JSON.parse(response);
    doc = extract_doc_from_conversation_response(response)

    context = TweetContext();
    context.descentants = parse_descendants(doc.getElementsByTagName('body')[0])
    context.continuation = obj.min_position
    return context

def parse_tweets_from_html(raw_html: bytes) -> TweetContext:
    """
    Given an API response about a particular tweet, parse and return the 
    TweetContext.
    """
    soup = extract_doc_from_response(raw_html)
    tweetContext = TweetContext()

    showMoreThreadsButton = doc.getElementsByClassName('ThreadedConversation-showMoreThreadsButton')[0]
    if (showMoreThreadsButton):
        tweetContext.continuation = showMoreThreadsButton.getAttribute('data-cursor')
    else:
        tweetContext.continuation = doc
            .querySelector('.replies-to .stream-container')
            .getAttribute('data-min-position')

    ancestorContainer = <HTMLElement>doc
        .getElementsByClassName('in-reply-to')[0];
    mainTweetContainer = <HTMLElement>doc
        .getElementsByClassName('permalink-tweet-container')[0];
    descendentsContainer = <HTMLElement>doc
        .getElementsByClassName('replies-to')[0];

    if ancestorContainer:
        tweetContext.ancestors = parseTweetsFromStream(ancestorContainer)

    if mainTweetContainer:
        tweetContext.tweet = parseTweetsFromStream(mainTweetContainer)[0]

    tweetContext.descentants = parseDescendants(descendentsContainer)
    return tweetContext

def parse_descendants(container: HTMLElement) -> List[List[Tweet]]:
    descendants = container
        .querySelectorAll('li.ThreadedConversation,li.ThreadedConversation--loneTweet')
    result = <Tweet[][]>[]

    for i in range(len(descendants)):
        let child = <HTMLElement>descendants[i]
        result.push(parseTweetsFromStream(child))
    return result

def extract_doc_from_response(raw_html: bytes) -> BeautifulSoup:
    soup = BeautifulSoup(raw_html, 'lxml', from_encoding="utf-8")
    return soup

def extract_doc_from_conversation_response(response: str) -> BeautifulSoup:
    let obj = JSON.parse(response);
    let responseHtml = obj.items_html || obj.descendants.items_html;
    let parser = new DOMParser();
    let doc = parser.parseFromString(responseHtml, 'text/html');
    return doc

def parse_tweets_from_stream(soup: BeautifulSoup) -> List[Tweet]:
    tweetStream = []
    tweetElements = soup.find_all("div", class_="tweet")

    #nextChildren = []
    for tweetElement in tweetElements:
        tweet = Tweet()
        
        tweet.username = tweetElement.['data-screen-name']
        
        tweet.name = tweetElement.find_all(attrs={'class':'fullname'})[0].string
        
        tweet.bodyText = tweetElement.find_all(attrs={'class':'tweet-text'})[0].string
        
        tweet.rtl = bool(len(tweetElement.find_all(attrs={'class':'tweet-text-rtl'})))
        
        tweet.bodyHtml = tweetElement.find_all(attrs={'class':'tweet-text'})[0].decode_contents()
        
        tweet.id = tweetElement.['data-tweet-id']
        
        tweet.avatar = tweetElement.find_all(attrs={'class':'avatar'})[0]['src']
        
        tweet.time = int(tweetElement.find_all(attrs={'class':'_timestamp'})[0]['data-time'])
        
        replies_str = tweetElement.find_all('button', attrs={'class':'js-actionReply'})[0].find_all('span', attrs={'class':'ProfileTweet-actionCountForPresentation'})[0].text
        try:
            replies_int = int(replies_str)
        except ValueError:
            replies_int = 0
        tweet.replies = replies_int

        for (let img of tweetElement.querySelectorAll('.AdaptiveMedia-photoContainer img'))
            tweet.images.push(img.getAttribute('src'))

        tweetStream.append(tweet)
        #nextChildren = [tweet.id]
    return tweetStream