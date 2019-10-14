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
import unidecode

from django.db.models import F
from django.db.utils import DatabaseError
from django.conf import settings

from moderation.moderate import addtoqueue
from bot.twitter import getAuth
from moderation.models import SocialUser, Category
from moderation.social import update_followersids
from community.models import Community, Retweet
from conversation.models import Hashtag
from .tasks import handle_retweetroot, handle_question
from .twitter import get_api

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


def has_retweet_hashtag( status ):
    """ Returns True if the tweet contains a hashtag that is in the retweet_hashtag_list.
    Returns False otherwise.
    In this function a "keyword" is always a hashtag. We must remove the #
    (first character) before comparing the string with the text of the hashtag entity.
    """
    if 'extended_tweet' in status:
        status = status['extended_tweet']
    #logger.debug("status in has_retweet_hashtag: %s", status)
    hashtags = [hashtag["text"].lower() for hashtag in status["entities"]["hashtags"]]
    #hashtag_retweet_list = [f"#{keyword}" for keyword in settings.KEYWORD_RETWEET_LIST]
    #ismatch = False
    #for hashtag in hashtags:
    #    for keyword in hashtag_retweet_list:
    #        if keyword[1:].lower() == hashtag["text"].lower():
    #            ismatch = True
    return HasRetweetHashtag(hashtags)

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

def is_following_rules(status):
    """
    Does this status follow the structural rules?
    * Is Not a retweet
    * Is a question
    * Is not a reply
    """  
    if isrt(status):
        return False

    if isreply(status):
        handle_retweetroot.apply_async(args=(status['id'],))
        return False

    if not isquestion(status):
        handle_question.apply_async(args=(status['id'],), countdown=10, expires=300) 
        return False

    return True

def isrt( status ):
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

def isreplacement( status ):
    "remove status asking for a replacement physician"
    if 'extended_tweet' in status:
        status = status['extended_tweet']
    text = status['full_text']
    #remplacementbadlist = frozenset([u"remplacement", u"rempla"])
    remplacantbadlist = frozenset(["rempla", "remplacant", "remplaçant"])
    monthlist = frozenset([u"janvier", u"fevrier", u"mars", u"avril", u"mai",
                          u"juin", u"juillet", u"aout", u"septembre",
                          u"octobre", u"novembre", u"decembre"])
    wordlist = frozenset(unidecode.unidecode(text).split())
    replacement = (bool(wordlist.intersection(monthlist)) and \
                     bool(wordlist.intersection(remplacantbadlist))) or \
                    (bool(wordlist.intersection(["du"])) and \
                     bool(wordlist.intersection(["au"])) and \
                     bool(wordlist.intersection(remplacantbadlist))) or \
                    (bool(wordlist.intersection(["cherche"])) and \
                     bool(wordlist.intersection(remplacantbadlist)))
    logger.debug("bool(replacement) == %s", bool(replacement))
    return bool(replacement)

def is_follower(userid, bot_screen_name):
    is_follower = userid in update_followersids(bot_screen_name, bot_screen_name=bot_screen_name)
    logger.info(f"5° is_follower: {is_follower}")
    return is_follower

def retweet(status_id) -> bool:
    api = tweepy.API(getAuth())
    try:
        api.retweet(status_id)
    except TweepError as e:
        logger.error(str(e))
        return False
    return True

def community_retweet(statusid: int, userid: int, hrh: HasRetweetHashtag):
    try:
        social_user = SocialUser.objects.get(user_id=userid)
    except SocialUser.DoesNotExist as e:
        logger.warn(f"SocialUser {userid} does not exist.", e)
        return
    category_qs = social_user.category.all()
    if not category_qs:
        return
    dct_lst = Retweet.objects.filter(retweet=True) \
                               .filter(category__in=category_qs) \
                               .filter(hashtag__in=hrh.hashtag_mi_lst) \
                               .values(
                                   _community=F('community'),
                                   _category=F('category'),
                                   _bot_screen_name=F('community__account__username')
                                ) \
                               .distinct()
    for dct in dct_lst:
        logger.debug(
            f'community: {dct["_community"]}'
            f'category: {dct["_category"]}'
            f'bot_screen_name: {dct["_bot_screen_name"]}'
        )
        if is_follower(userid, dct["_bot_screen_name"]):
            category = Category.objects.get(pk=dct["_category"])
            community = Community.objects.get(pk=dct['_community'])
            trusted_community_qs = community.trust.filter(category=category)
            trusted_community_lst = list(trusted_community_qs)
            trusted_community_lst.append(community)
            
            trust = False
            crs_lst = social_user.categoryrelationships.filter(category=category)
            for crs in crs_lst:
                if crs.community in trusted_community_lst:
                    trust = True
            
            if trust:
                get_api(username=dct["_bot_screen_name"]).retweet(statusid)
            else:
                addtoqueue(userid, statusid, community.name)
    
 
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
    return tweepy.Cursor(api.search,
                         q=get_search_string(),
                         lang=tweetLanguage,
                         tweet_mode='extended').items(settings.NUMBER_OF_RT)


def main():
    from .onstatus import triage 
    timelineIterator = timeline_iterator()
    current_sid = None
    for tweet in timelineIterator:
        triage(tweet.id)

def retweet_lst(lst):
    api = get_api()
    tw_counter = 0
    err_counter = 0
    for status in lst:
        try:
            logger.debug("(%(date)s) %(name)s: %(message)s\n" % \
                  {"date": status.created_at,
                   "name": status.author.screen_name.encode('utf-8'),
                   "message": status.full_text.encode('utf-8')})
    
            api.retweet(status.id)
            tw_counter += 1
        except tweepy.error.TweepError as e:
            # just in case tweet got deleted in the meantime or already retweeted
            err_counter += 1
            logger.debug("error: %s", e)
            continue
    
    logger.info("Finished. %d Tweets retweeted, %d errors occured." % (tw_counter, err_counter))
        
if __name__ == '__main__':
    main()