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
import os
import tweepy
from bot.twitter import getAuth
from bot.conf.cfg import getConfig
from bot.log.log import setup_logging
import logging
import unidecode
from moderation.models import SocialUser

setup_logging()
logger = logging.getLogger(__name__)

def has_retweet_hashtag( status ):
    """ Returns True if the tweet contains a hashtag that is in the retweet_hashtag_list.
    Returns False otherwise.
    In this function a "keyword" is always a hashtag. We must remove the #
    (first character) before comparing the string with the text of the hashtag entity.
    """
    if 'extended_tweet' in status:
        status = status['extended_tweet']
    #logger.debug("status in has_retweet_hashtag: %s", status)
    hashtags = status["entities"]["hashtags"]
    ismatch = False
    for hashtag in hashtags:
        for keyword in getConfig()["keyword_retweet_list"]:
            if keyword[1:].lower() == hashtag["text"].lower():
                ismatch = True
    return ismatch

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
    return '?' in status['full_text']

def okrt( status ):
    "should we RT this status?"
    if status['user']['id'] == getConfig()['settings']['bot_id']:
        logger.debug("self status, no RT")
        return False
    ok = not isrt(status) and \
         not isquote(status) and \
         not isreply(status) and \
         isauthorized(status) and \
         not isreplacement(status) and \
         not status['retweeted'] and \
         isquestion(status) and \
         has_retweet_hashtag(status)
    logger.debug("is this status ok for RT? %s", ok)
    logger.debug("Have I already RTed this? %s", status['retweeted'])
    print(status['retweeted'])
    return ok

def isrt( status ):
    "is this status a RT?"
    isrt = False
    isrt = "retweeted_status" in status
    logger.debug("is this status a retweet? %s" , isrt)
    return isrt

def isquote( status ):
    " is this a quoted status?"
    logger.debug("is this status a quoted status? %s" , status['is_quote_status'])
    return status['is_quote_status']

def isknown( status ):
    user_id = status['user']['id']
    if user_id not in SocialUser.objects.all_users():
        logger.debug("user %s UNKNOWN", user_id)
        return False
    logger.debug("user %s known", user_id)
    return True

def isauthorized( status ):
    return status['user']['id'] in SocialUser.objects.authorized_users()

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
    
def retweet( status_id ):
    api = tweepy.API(getAuth())
    api.retweet(status_id)
    return

if __name__ == '__main__':
    
    config = getConfig()
    # build savepoint path + file
    keyword_list = config["keyword_retweet_list"]
    search_string = " OR ".join ( keyword_list )
    search_string = search_string + u" -filter:retweets"
    logger.debug("search_string: %s" % (search_string))
    hashedHashtag = hashlib.md5(search_string.encode('ascii')).hexdigest()
    last_id_filename = "last_id_hashtag_%s" % hashedHashtag
    rt_bot_path = os.path.dirname(os.path.abspath(__file__))
    last_id_file = os.path.join(rt_bot_path, last_id_filename)
    
    # create bot
    api = tweepy.API(getAuth())
    
    # retrieve last savepoint if available
    try:
        with open(last_id_file, "r") as f:
            savepoint = f.read()
    except IOError:
        savepoint = ""
        logger.debug("No savepoint found. Bot is now searching for results")
    
    
    # Tweet language (empty = all languages)
    tweetLanguage = config["settings"]["tweet_language"]
    
    # search query
    timelineIterator = tweepy.Cursor(api.search, q=search_string, since_id=savepoint, lang=tweetLanguage, tweet_mode='extended').items(config["settings"]["number_of_rt"])
    
    # put everything into a list to be able to sort/filter
    
    oklist = []
    isRetweet = False
    
    for tweet in timelineIterator:
        status = api.get_status(tweet.id,  tweet_mode='extended')
        status_json = status._json
        logger.debug(" raw_status: %s", status._json)
        user = tweet.user
        screenname = user.screen_name
        userid = user.id
        useridstring = str(userid)
        status_text = tweet.full_text.encode('utf-8')
        logger.debug("userid: %s", userid)
        logger.debug("useridstring: %s", useridstring)
        logger.debug("screen name: %s", screenname)
        logger.debug("text: %s", tweet.full_text.encode('utf-8'))
        logger.debug("Is user authorized? %s", isauthorized(status_json))
        logger.debug("isrt: %s", isrt(status_json))
        logger.debug("status 'retweeted': %s", status_json['retweeted'])
        logger.debug("is this a question? %s", isquestion(status_json))
        if okrt(status_json):
            oklist.append(tweet)
            logger.debug(":) OK for RT")
        else:
            logger.debug(":( not ok for RT")
    
    try:
        last_tweet_id = oklist[0].id
    except IndexError:
        last_tweet_id = savepoint
    
    # filter bad words & users out and reverse timeline
    wordbadlist = set((u"remplacant",u"RT",u"remplaçant"))
    oklist = filter(lambda tweet: not any(word in tweet.full_text.split() for word in wordbadlist), oklist)
    
    oklist = list(oklist)
    oklist.reverse()
    
    tw_counter = 0
    err_counter = 0
    
    # iterate the timeline and retweet
    for status in oklist:
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
    
    # write last retweeted tweet id to file
    with open(last_id_file, "w") as f:
        f.write(str(last_tweet_id))
