import logging
from conversation.models import Tweetdj, Treedj
from django.db.utils import DatabaseError
from ..addstatusdj import addstatus
from ..doctoctocbot import retweet, isquestion, isauthorized, has_retweet_hashtag
from conversation.tree import tweet_parser, tweet_server
from bot.conf.cfg import getConfig
from moderation.models import SocialUser
from bot.tasks import handle_question

logger = logging.getLogger(__name__)

def retweetroot(statusid: int):
    """
    Starting from the status with statusid, analyze nodes towards root to
    determine if the root status should be retweeted.
    Retweet only if all nodes leading to root have the same author and if they contain a question mark
    """
    logger.debug(type(statusid))
    status_mi: Tweetdj = getorcreate(statusid)
    logger.debug(status_mi.json['full_text'])
    logger.debug(status_mi.json['in_reply_to_status_id'])
    logger.debug(status_mi.parentid)
    if status_mi.parentid is None:
        return

    has_rt_hashtag: bool = has_retweet_hashtag(status_mi.json)
    hasquestionmark: bool = isquestion(status_mi.json)
    logger.debug(f"hasquestionmark:{hasquestionmark}")
    authorid: int = status_mi.userid
    logger.debug(f"authorid:{authorid}")
    current_mi: Tweetdj = status_mi
    
    while True:
        
        parent_mi = getorcreate(current_mi.parentid)

        if parent_mi is None:
            break      
      
        if not hasquestionmark:
            hasquestionmark = isquestion(parent_mi.json)
            logger.debug(f"hasquestionmark:{hasquestionmark}")
        
        try:
            logger.debug(f"parent_mi.userid:{parent_mi.userid}") 
        except AttributeError:
            pass
        
        if not (parent_mi.userid == authorid):
            break
        if parent_mi.parentid is None:
            add_root_to_tree(parent_mi.statusid)
            if hasquestionmark:
                if isauthorized(parent_mi.json) and has_rt_hashtag:
                    retweet(parent_mi.statusid)
                break
            else:
                handle_question.apply_async(args=(statusid,), countdown=10, expires=300)
                break
        
        current_mi = parent_mi
        
    return

#def question(statusid):
#    raw_html = simple_get(f'https://twitter.com/statuses/{statusid}')
#    return raw_html

def add_root_to_tree(statusid):
    try:
        Treedj.objects.create(statusid=statusid)
    except DatabaseError as e:
        logger.error(str(e))
        
def getorcreate(statusid: int) -> Tweetdj:  
    # Is status in database? If not, add it.
    if statusid is None:
        logger.debug("statusid is None.")
        return None
    try:
        return Tweetdj.objects.get(pk=statusid)
    except Tweetdj.DoesNotExist:
        addstatus(statusid)
        return Tweetdj.objects.get(pk=statusid)

def has_questionmark(tweet: tweet_parser.Tweet) -> bool:
    return '?' in tweet.bodytext

def is_same_author(tweet0: tweet_parser.Tweet, tweet: tweet_parser.Tweet) -> bool:        
    return tweet0.userid == tweet.userid
     
def question(statusid: int) -> bool:
    logger.debug(f"Running question() with statusid {statusid}")
    tweet0 = tweet_parser.Tweet(statusid)
    logger.debug(f"Object:{tweet0}, statusid:{tweet0.statusid}")
    tweet_context = tweet_server.request_tweets(tweet0)
    hashtag_tweet = tweet_context.tweet
    has_rt_hashtag = _has_retweet_hashtag(hashtag_tweet)
    
    start_tweet = tweet_parser.Tweet(hashtag_tweet.conversationid)
    start_tweet_context = tweet_server.request_tweets(start_tweet)
    start_tweet = start_tweet_context.tweet
    
    logger.debug(f"Object:{hashtag_tweet}, statusid: {hashtag_tweet.statusid}, bodytext: {hashtag_tweet.bodytext}")
    descendants = tweet_context.descendants
    logger.debug(f"{descendants}, {len(descendants)}")
    for lst_tweet in tweet_context.descendants:
        logger.debug(f"{lst_tweet}, {len(lst_tweet)}")
        for tweet in lst_tweet:
            logger.debug(f"\n{tweet.statusid}\n{tweet.bodytext}\n conversationid: {tweet.conversationid}")
            logger.debug(f"has_questionmark: {has_questionmark(tweet)}")
            logger.debug(f"init_author: {hashtag_tweet.userid}\n author:{tweet.userid}")
            logger.debug(f"is_same_author: {is_same_author(hashtag_tweet, tweet)}")
            if has_questionmark(tweet) and is_same_author(hashtag_tweet, tweet):
                if hashtag_tweet.statusid == tweet.conversationid:
                    add_root_to_tree(hashtag_tweet.statusid)
                    if _isauthorized(hashtag_tweet) and has_rt_hashtag:
                        retweet(hashtag_tweet.statusid)
                    return True
                elif is_same_author(hashtag_tweet, start_tweet):
                    add_root_to_tree(start_tweet.statusid)
                    if _isauthorized(start_tweet) and has_rt_hashtag:
                        retweet(start_tweet.statusid)
                    return True
    return False

def _isauthorized(tweet: tweet_parser.Tweet) -> bool:
    logger.debug(f"list: {SocialUser.objects.authorized_users()}")
    logger.debug(f"userid: {tweet.userid}, type: {type(tweet.userid)}")
    logger.debug(f"bool:{tweet.userid in SocialUser.objects.authorized_users()}")
    return tweet.userid in SocialUser.objects.authorized_users()

def _has_retweet_hashtag(tweet: tweet_parser.Tweet) -> bool:
    """ Returns True if the tweet contains a hashtag that is in the retweet_hashtag_list.
    Returns False otherwise.
    """
    ismatch = False
    for keyword in getConfig()["keyword_retweet_list"]:
        logger.debug(f"keyword.lower():{keyword.lower()} txt.lower():{tweet.bodytext.lower()}")
        if keyword.lower() in tweet.bodytext.lower():
            ismatch = True
    return ismatch