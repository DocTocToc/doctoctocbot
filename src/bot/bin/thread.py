from django.db.utils import DatabaseError, IntegrityError
import logging

from bot.tasks import handle_question
from conversation.models import Tweetdj, Treedj, create_tree
from conversation.tree import tweet_parser, tweet_server
from moderation.models import SocialUser
from community.models import Retweet 
from django.conf import settings
import tweepy
from bot.tweepy_api import get_api
from conversation.models import create_leaf
from conversation.tree.utils import StatusTree

from ..addstatusdj import addstatus
from ..doctoctocbot import (
    community_retweet,
    isquestion,
    isquote,
    has_retweet_hashtag,
    HasRetweetHashtag,
    tree_hrh,
)


logger = logging.getLogger(__name__)

def retweetroot(statusid: int, bot_screen_name: str):
    """
    Starting from the status with statusid, analyze nodes towards root to
    determine if the root status should be retweeted.
    Retweet only if all nodes leading to root have the same author and if they
    contain a question mark
    """
    status_mi: Tweetdj = getorcreate(statusid, bot_username=bot_screen_name)
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
        parent_mi = getorcreate(
            current_mi.parentid,
            bot_username=bot_screen_name
        )
        logger.info(f'{parent_mi=}')
        if not parent_mi:
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
                if (hrh and not isquote(parent_mi.json)):
                    community_retweet(
                        parent_mi.statusid,
                        parent_mi.userid,
                        hrh,
                        skip_rules=True
                    )
                    break
            else:
                handle_question.apply_async(
                    args=(statusid,bot_screen_name,),
                    countdown=30,
                    expires=900
                )
                break
        current_mi = parent_mi
    return

def tree_has_question_mark(tweetdj: Tweetdj, bot_username=None):
    """Return True if the tree contains a status with a question mark
    created by the author of the root node
    """
    if tweetdj_has_q_m(tweetdj):
        return True
    root_tweetdj = get_root_status(tweetdj, bot_username=bot_username)
    if tweetdj_has_q_m(root_tweetdj):
        return True
    # get all descendants of root status with same author
    st = StatusTree(statusid=root_tweetdj.statusid)
    statusids = st.root_user_nodes().values_list("statusid", flat=True)
    for tweetdj in Tweetdj.objects.filter(statusid__in=statusids):
        if tweetdj_has_q_m(tweetdj):
            return True
        
def get_root_status(tweetdj: Tweetdj, bot_username=None):
    userid = tweetdj.userid
    if not tweetdj.parentid:
        return tweetdj
    parent_mi = getorcreate(
        tweetdj.parentid,
        bot_username=bot_username,
    )
    if not parent_mi:
        return tweetdj
    if not parent_mi.userid == userid:
        return
    return get_root_status(parent_mi, bot_username=bot_username)

def add_root_to_tree(statusid):
    try:
        Treedj.objects.create(statusid=statusid)
    except IntegrityError as e:
        logger.error(f"Integrity error: {e}")
    except DatabaseError as e:
        logger.error(f" Database error: {e}")

def getorcreate(statusid: int, bot_username=None) -> Tweetdj:
    # Is status in database? If not, add it.
    if statusid is None:
        return
    try:
        return Tweetdj.objects.get(statusid=statusid)
    except Tweetdj.DoesNotExist:
        addstatus(
            statusid,
            bot_username=bot_username
        )
        try:
            return Tweetdj.objects.get(statusid=statusid)
        except Tweetdj.DoesNotExist:
            return

def has_questionmark(tweet: tweet_parser.Tweet) -> bool:
    return '?' in tweet.bodytext

def tweetdj_has_q_m(tweetdj):
    status = tweetdj.json
    if not status:
        return False
    if 'extended_tweet' in status:
        status = status['extended_tweet']
    return '?' in status["full_text"]

def is_same_author(tweet0: tweet_parser.Tweet, tweet: tweet_parser.Tweet) -> bool:        
    return tweet0.userid == tweet.userid

def add_leaf(node_id, parent_id):
    try:
        parent = Treedj.objects.get(statusid=parent_id)
    except Treedj.DoesNotExist:
        return
    try:
        Treedj.objects.create(
            statusid=node_id,
            parent=parent
        )
    except IntegrityError as e:
        logger.debug(f"Integrity error: {e}")
    except DatabaseError as e:
        logger.debug(f" Database error: {e}")

def question_api(start_status_id: int, bot_username: str) -> bool:
    try:
        start_tweetdj = Tweetdj.objects.get(statusid=start_status_id)
    except Tweetdj.DoesNotExist:
        return
    logger.debug(f'start_tweetdj: {start_tweetdj}')
    socialuser = start_tweetdj.socialuser
    logger.debug(f'socialuser: {socialuser}')
    if not socialuser:
        return
    userid = socialuser.user_id
    logger.debug(f'userid: {userid}')
    api = get_api(username=bot_username)
    root_tweetdj = get_root_status(
        start_tweetdj,
        bot_username=bot_username,
    )
    if not root_tweetdj:
        return
    tree_has_q_m: bool = tree_has_question_mark(
        start_tweetdj,
        bot_username=bot_username
    )
    hrh = tree_hrh(start_tweetdj, bot_username=bot_username)
    if tree_has_q_m and hrh: 
        community_retweet(root_tweetdj.statusid, userid, hrh, skip_rules=True)
        return True
    try:
        treedj, _created = Treedj.objects.get_or_create(
            statusid=root_tweetdj.statusid
        )
    except IntegrityError as e:
        logger.error(f"Integrity error: {e}")
    except DatabaseError as e:
        logger.error(f" Database error: {e}")
    descendants_id_lst = (
        treedj.get_descendants(include_self=True)
        .values_list("statusid", flat=True)
    )
    for status in tweepy.Cursor(api.user_timeline, 
                        user_id=userid, 
                        count=None,
                        since_id=root_tweetdj.statusid,
                        max_id=None,
                        trim_user=True,
                        exclude_replies=False,
                        ).items():
        reply_id = status._json.get("in_reply_to_status_id", None)
        logger.debug(f'reply_id: {reply_id}')
        if not reply_id:
            continue
        if reply_id in descendants_id_lst:
            status_id = status._json["id"]
            add_leaf(status_id, reply_id)
            tweetdj = getorcreate(status_id, bot_username=bot_username)
            if not tweetdj:
                continue
            hrh = tree_hrh(tweetdj, bot_username=bot_username)
            logger.debug(f'hrh: {hrh}')
            q = tree_has_question_mark(tweetdj)
            logger.debug(f'q:{q}')
            if q and hrh:
                #logger.debug(
                #    f'status {status._json["id"]} '
                #    f'{status._json["text"]} is ?'
                #)
                community_retweet(
                    root_tweetdj.statusid,
                    userid,
                    hrh,
                    skip_rules=True
                )
                return True

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