from django.db.utils import DatabaseError
import logging

from bot.tasks import handle_question
from conversation.models import Tweetdj, Treedj, create_tree
from conversation.tree import tweet_parser, tweet_server
from moderation.models import SocialUser
from community.models import Retweet 
from django.conf import settings
import tweepy
from bot.twitter import get_api
from conversation.models import create_leaf

from ..addstatusdj import addstatus
from ..doctoctocbot import (
    community_retweet,
    isquestion,
    isreplacement,
    isquote,
    has_retweet_hashtag,
    HasRetweetHashtag
)


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

    hrh = has_retweet_hashtag(status_mi.json)
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
                if (hrh \
                    and not isreplacement(parent_mi.json) \
                    and not isquote(parent_mi.json)):
                    community_retweet(parent_mi.statusid, parent_mi.userid, hrh)
                    break
            else:
                handle_question.apply_async(args=(statusid,), countdown=10, expires=300)
                break
        
        current_mi = parent_mi
        
    return

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

def question_api(statusid: int) -> bool:
    try:
        socialuser = Tweetdj.objects.get(statusid=statusid).socialuser
    except Tweetdj.DoesNotExist:
        return
    community = socialuser.community()
    if not community:
        return
    try:
        bot_username = community.account.username
    except:
        return
    api = get_api(username=bot_username, backend=True)
    treedj, _created = Treedj.objects.get_or_create(statusid=statusid)
    descendants_id_lst = (
        treedj.get_descendants(include_self=True)
        .values_list("statusid", flat=True)
    )
    for status in tweepy.Cursor(api.user_timeline, 
                        user_id=socialuser.user_id, 
                        count=None,
                        since_id=statusid,
                        max_id=None,
                        trim_user=True,
                        exclude_replies=False,
                        ).items():
        reply_id = status._json.get("in_reply_to_status_id", None)
        if not reply_id:
            continue
        if reply_id in descendants_id_lst:
            if "?" in status._json["text"]:
                logger.debug(
                    f'status {status._json["id"]} '
                    f'{status._json["text"]} is ?'
                )
                return True
            try:
                parent = Treedj.objects.get(statusid=reply_id)
            except Treedj.DoesNotExist:
                continue 
            try:
                Treedj.objects.create(
                    statusid=status._json["id"],
                    parent=parent
                )
            except DatabaseError:
                continue
        
     
def question(statusid: int) -> bool:
    logger.debug(f"Running question() with statusid {statusid}")
    tweet0 = tweet_parser.Tweet(statusid)
    logger.debug(f"Object:{tweet0}, statusid:{tweet0.statusid}")
    tweet_context = tweet_server.request_tweets(tweet0)
    hashtag_tweet = tweet_context.tweet
    hrh = _has_retweet_hashtag(hashtag_tweet)
    
    start_tweet = tweet_parser.Tweet(hashtag_tweet.conversationid)
    start_tweet_context = tweet_server.request_tweets(start_tweet)
    if not start_tweet_context:
        return False
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
                    if hrh:
                        community_retweet(hashtag_tweet.statusid, hashtag_tweet.userid, hrh)
                    return True
                elif is_same_author(hashtag_tweet, start_tweet):
                    add_root_to_tree(start_tweet.statusid)
                    if hrh:
                        community_retweet(start_tweet.statusid, start_tweet.userid, hrh)
                    return True
    return False

def _has_retweet_hashtag(tweet: tweet_parser.Tweet) -> bool:
    """ Returns True if the tweet contains a hashtag that is in the retweet_hashtag_list.
    Returns False otherwise.
    """
    hrh = HasRetweetHashtag()
    tags = Retweet.objects.filter(retweet=True).values_list('hashtag__hashtag', flat=True)
    hashtags = [f"#{tag}" for tag in tags]
    logger.debug("hashtag retweet list: %s", hashtags)
    for hashtag in hashtags:
        logger.debug(f"hashtag.lower():{hashtag.lower()} txt.lower():{tweet.bodytext.lower()}")
        if hashtag.lower() in tweet.bodytext.lower():
            hrh.add(hashtag[1:])
    return hrh