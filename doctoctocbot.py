#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Bot to enhance french healthcare professionals exchanges on Twitter.

Author: Jérome Pinguet.
Based on [retweet-bot](https://github.com/basti2342/retweet-bot) by [Basti](https://github.com/basti2342)
License: Mozilla Public License, see 'LICENSE' for details.
"""

import hashlib
import os
import tweepy
from twitter import getAuth
from cfg import getConfig
from log import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

def whatisthis(s):
    if isinstance(s, str):
        print("ordinary string")
    elif isinstance(s, unicode):
        print("unicode string")
    else:
        print("not a string")

def isreply( status ):
    "is status in reply to screen name or status or user?"
    logger.debug("in_reply_to_screen_name? %s" , status['in_reply_to_screen_name'])
    logger.debug("in_reply_to_status_id_str? %s" , status['in_reply_to_status_id_str'])
    logger.debug("in_reply_to_user_id_str? %s" , status['in_reply_to_user_id_str'])
    reply_screen = str(status['in_reply_to_screen_name'])
    reply_id = str(status['in_reply_to_status_id_str'])
    reply_user = str(status['in_reply_to_user_id_str'])
    logger.debug(whatisthis(reply_screen))
    logger.debug(whatisthis(reply_id))
    logger.debug(whatisthis(reply_user))
    isreply = not (reply_screen == "None" and
               reply_id == "None" and
               reply_user == "None")
    log = "is this status a reply? %s" % isreply
    logger.debug(log)
    return isreply

def okrt( status ):
    "should we RT this status?"
    ok = not isrt(status) and \
         not isquote(status) and \
         not isreply(status) and \
         iswhitelist(status) and \
         okblacklist(status)
    logger.debug("is this status ok for RT?")
    logger.debug(ok)
    logger.debug(type(ok))
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

def iswhitelist( status ):
    "is the author of the status whitelisted?"
    logger.debug("user id: %s", status['user']['id'])
    return status['user']['id'] in getWhitelist()

def lenWhitelist():
    "length of whitelist"
    logger.debug("Number of users in white list: %s", len(getWhitelist))
    return len(getWhitelist)

def okblacklist( status ):
    "filter blacklisted words"
    wordBlacklist = set((u"remplacant",u"RT",u"remplaçant"))
    logger.debug("Does text contain blacklisted word? %s", any(word in status['text'].split() for word in wordBlacklist))
    return not any(word in status['text'].split() for word in wordBlacklist)

def retweet( status_id ):
    api = tweepy.API(getAuth())
    api.retweet(status_id)
    return

def getWhitelist():
    "get user whitelist"
    whitelistfilename = getConfig()["whitelist"]["file"]
    with open(whitelistfilename, 'r') as f:
        whitelist = [int(line.rstrip('\n')) for line in f]
    logger.debug(whitelist)
    return whitelist

if __name__ == '__main__':
    
    config = getConfig()
    # build savepoint path + file
    hashtag = config["settings"]["search_query"]
    hashedHashtag = hashlib.md5(hashtag.encode('ascii')).hexdigest()
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
        print("No savepoint found. Bot is now searching for results")
    
    
    # your hashtag or search query and tweet language (empty = all languages)
    tweetLanguage = config["settings"]["tweet_language"]
    
    # search query
    timelineIterator = tweepy.Cursor(api.search, q=hashtag, since_id=savepoint, lang=tweetLanguage).items(config["settings"]["number_of_rt"])
    
    # put everything into a list to be able to sort/filter
    
    oklist = []
    isRetweet = False
    
    for tweet in timelineIterator:
        isRetweet = False
        user = tweet.user
        screenname = user.screen_name
        userid = user.id
        useridstring = str(userid)
        status_text = tweet.text.encode('utf-8')
        logger.debug("userid: %s", userid)
        logger.debug("useridstring: %s", useridstring)
        logger.debug("screen name: %s", screenname)
        logger.debug("useridstring in whitelist? %s", (useridstring in getWhitelist()))
        if hasattr(tweet, 'retweeted_status'):
            isRetweet = True
            logger.debug("retweet: %s", isRetweet)
        logger.debug("text: %s", tweet.text.encode('utf-8'))
        logger.debug("useridstring in whitelist: %s", (iswhitelist(tweet._json)))
        logger.debug("not isRetweet: %s", not isRetweet)
        if (iswhitelist(tweet._json) and (not isRetweet)):
            oklist.append(tweet)
            logger.debug("User in whitelist AND status not a RT: OK for RT")
        else:
            logger.debug("not ok for RT")
    
    
    try:
        last_tweet_id = oklist[0].id
    except IndexError:
        last_tweet_id = savepoint
    
    # filter blacklisted words & users out and reverse timeline
    wordBlacklist = set((u"remplacant",u"RT",u"remplaçant"))
    oklist = filter(lambda tweet: not any(word in tweet.text.split() for word in wordBlacklist), oklist)
    
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
                   "message": status.text.encode('utf-8'),
                   "retweeted": isRetweet})
    
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