#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Bot to enhance French healthcare professionals exchanges on Twitter.

Author: Jérome Pinguet.
License: GNU General Public License version 3 (see 'LICENSE' for details.)

DocTocTocBot started as a modification of the single file [retweet-bot](https://github.com/basti2342/retweet-bot)
by [Basti](https://github.com/basti2342) License: Mozilla Public License version 2.0
  * timelineIterator
  * savepoint
  * RT for loop with error & RT counters
"""

import hashlib
import logging
import os
import tweepy
from tweepy.error import TweepError

from django.db.models import F, Q
from django.db.utils import DatabaseError
from django.conf import settings

from bot.addstatusdj import addstatus
from bot.tweepy_api import getAuth
from moderation.models import SocialUser, Category
from moderation.social import update_social_ids
from community.models import Community, Retweet
from conversation.models import Hashtag, Tweetdj, Retweeted
from .tasks import handle_retweetroot, handle_question
from bot.tweepy_api import get_api
from moderation.moderate import process_unknown_user
from bot.tweet import hashtag_list
from tagging.tasks import keyword_tag
from bot.models import Account
from conversation.models import create_tree
from filter.process import filter_status
from conversation.utils import donotretweet

logger = logging.getLogger(__name__)


class HasRetweetHashtag(object):
    try:
        hashtags = [ht.lower() for ht in Retweet.objects.filter(retweet=True).values_list('hashtag__hashtag', flat=True)]
    except DatabaseError as e:
        logger.warn(e)
        hashtags= list()

    def __init__(self, data=None):
        self.hashtag_mi_lst = []
        self.hashtag_lst = []
        if data:
            self.add(data)
        
    def __bool__(self):
        return bool(len(self.hashtag_lst))
    
    def add(self, data):
        if isinstance(data, str):
            ht = data.lower()
            if ht in self.hashtags:
                self.hashtag_lst.append(ht)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    ht = item.lower()
                    if ht in self.hashtags:
                        self.hashtag_lst.append(ht)
        else:
            return
        self.add_hashtag_mi()
        
    def add_hashtag_mi(self):
        try:
            for hashtag_mi in Hashtag.objects.filter(hashtag__in=self.hashtag_lst):
                self.hashtag_mi_lst.append(hashtag_mi)
        except DatabaseError as e:
            logger.error(e)

def has_retweet_hashtag(status):
    """ Returns HasRetweetHashtag object
    In this function a "keyword" is always a hashtag. We must remove the #
    (first character) before comparing the string with the text of the hashtag entity.
    """
    hashtags = hashtag_list(status)
    return HasRetweetHashtag(hashtags)

def tree_hrh(tweetdj, hrh=None) -> HasRetweetHashtag:
    def getorcreate(statusid: int) -> Tweetdj:  
        # Is status in database? If not, add it.
        if statusid is None:
            logger.debug("statusid is None.")
            return None
        try:
            return Tweetdj.objects.get(pk=statusid)
        except Tweetdj.DoesNotExist:
            addstatus(statusid)
            try:
                return Tweetdj.objects.get(pk=statusid)
            except Tweetdj.DoesNotExist:
                return None
    if hrh is None:
        hrh = has_retweet_hashtag(tweetdj.json)
    elif isinstance(hrh, HasRetweetHashtag):
        hrh.add(hashtag_list(tweetdj.json))
    else:
        return HasRetweetHashtag()
    if not tweetdj.parentid:
        return hrh
    parent: Tweetdj = getorcreate(tweetdj.parentid)
    return tree_hrh(parent, hrh)

def isreply( status ):
    "is status in reply to screen name or status or user?"
    logger.debug("in_reply_to_screen_name? %s" , status['in_reply_to_screen_name'])
    logger.debug("in_reply_to_status_id_str? %s" , status['in_reply_to_status_id_str'])
    logger.debug("in_reply_to_user_id_str? %s" , status['in_reply_to_user_id_str'])
    reply_screen = str(status['in_reply_to_screen_name'])
    reply_id = str(status['in_reply_to_status_id_str'])
    reply_user = str(status['in_reply_to_user_id_str'])
    isreply = not (reply_screen == "None" and
               reply_id == "None" and
               reply_user == "None")
    log = "is this status a reply? %s" % isreply
    logger.debug(log)
    return isreply

def isquestion ( status ):
    "Does this status text contain a question mark?"
    if 'extended_tweet' in status:
        status = status['extended_tweet']
    isquestion = '?' in status['full_text']
    return isquestion

def isretweeted(status):
    return status['retweeted']

def is_following_rules(statusid, userid, dct):
    try:
        tweetdj = Tweetdj.objects.get(statusid=statusid)
        return is_following_rules_json(tweetdj.json, userid, dct)
    except Tweetdj.DoesNotExist:
        return False

def is_following_rules_json(status, userid, dct):
    """
    Does this status follow the structural rules?
    """
    if dct["_require_follower"] and not is_follower(userid, dct["_bot_screen_name"]):
        return False
    if isrt(status) and not dct["_allow_retweet"]:
        return False
    if isquote(status) and not dct["_allow_quote"]:
        return False
    if isreply(status):
        handle_retweetroot.apply_async(args=(status['id'],))
        return False
    if dct["_require_question"] and not isquestion(status):
        logger.debug(f"status['id']: {status['id']}")
        handle_question.apply_async(args=(status['id'],), countdown=30, expires=900) 
        return False
    return True

def isrt(status):
    "is this status a RT?"
    isrt = "retweeted_status" in status.keys()
    logger.debug("is this status a retweet? %s" , isrt)
    return isrt

def isquote( status ):
    " is this a quoted status?"
    logger.debug("is this status a quoted status? %s" , status['is_quote_status'])
    return status['is_quote_status']

def isknown( status ):
    user_id = status['user']['id']
    try:
        social_user = SocialUser.objects.get(user_id=user_id)
    except SocialUser.DoesNotExist:
        return False
    isknown = bool(social_user.category.all())
    logger.info(f"user {user_id} isknown: {isknown}")
    return isknown

def okbadlist( status ):
    "filter bad words"
    if 'extended_tweet' in status:
        status = status['extended_tweet']
    wordbadlist = set((u"remplacant",u"RT",u"remplaçant"))
    logger.debug("Does text contain bad words? %s", any(word in status['full_text'].split() for word in wordbadlist))
    return not any(word in status['full_text'].split() for word in wordbadlist)



def is_follower(userid, bot_screen_name):
    try:
        account = Account.objects.get(username=bot_screen_name)
        logger.debug(f"{account}")
    except Account.DoesNotExist:
        return
    community = account.community
    logger.debug(f"{community}")
    if not community:
        return
    follower_common_accounts = [account]
    logger.debug(f"{follower_common_accounts}")
    follower_common_accounts.extend(list(community.follower_common_account.all()))
    logger.debug(f"{follower_common_accounts}")
    _is_follower = False
    for follower_common_account in follower_common_accounts:
        bot_screen_name = follower_common_account.username
        bot_userid = follower_common_account.userid
        try:
            _is_follower = userid in update_social_ids(
                bot_userid,
                cached=True,
                bot_screen_name=bot_screen_name,
                relationship='followers',
            )
            logger.debug(f"_is_follower: {_is_follower}")
            # break early if True
            if _is_follower:
                return _is_follower
        except TypeError:
            continue
    return _is_follower

def create_update_retweeted(statusid, community, retweet_status):
    rt: Retweeted = Retweeted.objects.as_of().filter(
        status=statusid,
        account=community.account,
    ).first()
    if rt:
        rt = Retweeted.objects.current_version(retweet)
        if rt.status == statusid and rt.retweet == retweet_status["id"]:
            return
        else:
            retweet = retweet.clone()
            retweet.retweet = retweet_status["id"]
            retweet.save()
            return
    try:
        Retweeted.objects.create(
            status=statusid,
            account=community.account,
            retweet=retweet_status["id"],  
        )
    except:
        return

def community_retweet(
        statusid: int,
        userid: int, hrh: HasRetweetHashtag,
        skip_rules=False
    ):
    logger.debug("Inside community_retweet()")
    logger.debug(statusid)
    logger.debug(userid)
    logger.debug(f"hrh: {hrh}; hrh.hashtag_mi_lst: {hrh.hashtag_mi_lst}")
    try:
        social_user = SocialUser.objects.get(user_id=userid)
        logger.debug(social_user)
    except SocialUser.DoesNotExist as e:
        logger.warn(f"SocialUser {userid} does not exist.", e)
        social_user = None
    
    if social_user:
        category_qs = social_user.category.all()
        logger.debug(f"category_qs: {category_qs}")
        logger.debug(f"bool(category_qs): {bool(category_qs)}")

    else:
        category_qs = []
        logger.debug(f"category_qs: {category_qs}")

    process_unknown_lst = Retweet.objects.filter(retweet=True) \
        .filter(hashtag__in=hrh.hashtag_mi_lst) \
        .values(
            _community=F('community'),
            _category=F('category'),
            _bot_screen_name=F('community__account__username'),
            _moderation=F('moderation'),
            _require_question=F('require_question'),
            _allow_retweet=F('allow_retweet'),
            _allow_quote=F('allow_quote'),
            _allow_unknown=F('community__allow_unknown'),
            _require_follower=F('require_follower'),
            _favorite=F('favorite'),
            _retweet=F('retweet'),
        ).order_by('community').distinct('community')
    logger.debug(f"process_unknown_lst: {process_unknown_lst}")
    #process unknown user
    for dct in process_unknown_lst:
        logger.debug(f"process_unknown dct: {dct}")
        rules =  skip_rules or is_following_rules(statusid, userid, dct)
        logger.debug(f"rules: {rules}")
        logger.debug(f"dct['_allow_unknown']: {dct['_allow_unknown']}")
        if (rules
            and not category_qs
            and not dct["_allow_unknown"]):
            logger.debug("calling process_unknown_user() ...")
            process_unknown_user(userid, statusid, hrh)
    # process retweet
    process_retweet_lst = process_unknown_lst.filter(
        Q(category__isnull=True) | Q(category__in=category_qs)
    )
    logger.debug(f"process_retweet_lst: {process_retweet_lst}")
    for dct in process_retweet_lst:
        # process unknown user
        logger.debug(f"dct: {dct}")
        logger.debug(
            f'community: {dct["_community"]},\n'
            f'category: {dct["_category"]},\n'
            f'bot_screen_name: {dct["_bot_screen_name"]},\n'
            f'moderation: {dct["_moderation"]},\n'
            f'allow_retweet: {dct["_allow_retweet"]},\n'
            f'allow_quote: {dct["_allow_quote"]},\n'
            f'allow_unknown: {dct["_allow_unknown"]},\n'
            f'require_follower: {dct["_require_follower"]},\n'
            f'{dct["_favorite"]=},\n'
            f'{dct["_retweet"]=},\n'
        )
        try:
            community = Community.objects.get(pk=dct['_community'])
            logger.debug(f"community: {community}")
        except Community.DoesNotExist:
            logger.error(f"Community {dct['_community']} does not exist.")
            continue
        if not dct["_moderation"]:
            if skip_rules or is_following_rules(statusid, userid, dct):
                rt(statusid, dct, community)
        if not social_user:
            continue
        category = Category.objects.get(pk=dct["_category"])
        logger.debug(f"category:{category}")
        trusted_community_qs = community.trust.filter(category=category)
        trusted_community_lst = list(trusted_community_qs)
        logger.debug(f"trusted_community_lst:{trusted_community_lst}")
        # if community forgot to trust itself:
        trusted_community_lst.append(community)
        logger.debug(f"trusted_community_lst:{trusted_community_lst}")
        
        trust = False
        crs_lst = (
            social_user.categoryrelationships
            .filter(category=category)
            .exclude(moderator=social_user)
        )
        logger.debug(f"crs_lst:{crs_lst}")
        for crs in crs_lst:
            if crs.community in trusted_community_lst:
                trust = True
        
        if trust:
            if skip_rules or is_following_rules(statusid, userid, dct):
                rt(statusid, dct, community)

def create_tree_except_rt(statusid):
    try:
        tweetdj = Tweetdj.objects.get(statusid=statusid)
    except Tweetdj.DoesNotExist:
        return
    if not tweetdj.retweetedstatus and not tweetdj.parentid:
        create_tree(statusid)


def rt(statusid, dct, community):
    logger.info(
        f"Retweeting status: {statusid}\n"
        f"for community: {community.name}\n"
        f"with dct: {dct}\n"
    )
    flag = filter_status(statusid=statusid, community=community)
    if flag:
        logger.warn(
            f"Status {statusid} triggered the '{flag.filter}' filter. "
            "Retweet canceled."
        )
        return
    if donotretweet(statusid, community):
        logger.warn(
            f"Status {statusid} for {community} has an active "
            "DoNotRetweetStatus record: retweet canceled."
        )
        return
    username = dct["_bot_screen_name"]
    api = get_api(username=username, backend=True)
    if community.active:
        if dct["_retweet"]:
            try:
                res = api.retweet(statusid)
                logger.info(
                    f"I just retweeted status {statusid}\n"
                    f"Response: {res}"
                )
            except TweepError as e:
                logger.error(
                    f"Error during retweet of status {statusid}:\n{e}"
                )
                res = None
            if res:
                set_retweeted_by(statusid, community)
                create_update_retweeted(statusid, community, res._json)
        if dct["_favorite"]:
            try:
                res = api.create_favorite(statusid)
                logger.info(
                    f"I just favorited status {statusid}\n"
                    f"Response: {res}"
                )
            except TweepError as e:
                logger.error(
                    f"Error during favorite of status {statusid}:\n{e}"
                )
    else:
        logger.info(
            f"I did not retweet and/or favorite status {statusid} because "
            f"{community} is not active\n"
        )
    keyword_tag(statusid, community)

def set_retweeted_by(statusid: int, community):
    try:
        user_id = community.account.userid
    except:
        return
    try:
        su: SocialUser = SocialUser.objects.get(user_id=user_id)
    except SocialUser.DoesNotExist:
        return
    try:
        tweetdj = Tweetdj.objects.get(statusid=statusid)
    except Tweetdj.DoesNotExist:
        return
    tweetdj.retweeted_by.add(su)

def get_search_string():
    keyword_list = settings.KEYWORD_RETWEET_LIST
    search_string = " OR ".join ( keyword_list )
    search_string = search_string + u" -filter:retweets"
    logger.debug("search_string: %s" % (search_string))
    return search_string

def last_id_file():
    hashedHashtag = hashlib.md5(get_search_string().encode('ascii')).hexdigest()
    last_id_filename = "last_id_hashtag_%s" % hashedHashtag
    rt_bot_path = os.path.dirname(os.path.abspath(__file__))
    last_id_file = os.path.join(rt_bot_path, last_id_filename)
    return last_id_file 

def save_point():
    # retrieve last savepoint if available
    pass
    """
    try:
        with open(last_id_file(), "r") as f:
            savepoint = f.read()
    except IOError:
        savepoint = ""
        logger.debug("No savepoint found. Bot is now searching for results")

    return savepoint
    """
    
def timeline_iterator():    
    # Tweet language (empty = all languages)
    tweetLanguage = settings.TWEET_LANGUAGE
    
    api = get_api()
    if not api:
        return   
    return tweepy.Cursor(api.search,
                         q=get_search_string(),
                         lang=tweetLanguage,
                         tweet_mode='extended').items(settings.NUMBER_OF_RT)


def main():
    from .onstatus import triage 
    timelineIterator = timeline_iterator()
    for tweet in timelineIterator:
        triage(tweet.id)

if __name__ == '__main__':
    main()