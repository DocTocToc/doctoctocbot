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
from cfg import getConfig, whitelist
from log import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)


def getAuth( ):
    "get Tweepy OAuthHandler authentification object"
    config = getConfig()
    auth = tweepy.OAuthHandler(config.get("twitter", "consumer_key"), config.get("twitter", "consumer_secret"))
    auth.set_access_token(config.get("twitter", "access_token"), config.get("twitter", "access_token_secret"))
    return auth


def okrt( status ):
    "should we RT this status?"
    return not isrt(status) and iswhitelist(status) and okblacklist(status) 

def isrt( status ):
    "is this status a RT?"
    logger.debug("is this status a retweet? %s" , status['retweeted'])
    return status['retweeted']

def iswhitelist( status ):
    "is the author of the status whitelisted?"
    logger.debug("user id: %s", status['user']['id'])
    return status['user']['id'] in whitelist

def lenWhitelist():
    "length of whitelist"
    logger.debug("Number of users in white list: %s", len(cfg.whitelist))
    return len(whitelist)

def okblacklist( status ):
    "filter blacklisted words"
    wordBlacklist = set((u"remplacant",u"RT",u"remplaçant"))
    logger.debug("Does text contain blacklisted word? %s", any(word in status['text'].split() for word in wordBlacklist))
    return not any(word in status['text'].split() for word in wordBlacklist)

def retweet( id ):
    api = tweepy.API(getAuth())
    api.retweet(id)
    return


if __name__ == '__main__':

    # build savepoint path + file
    hashtag = getConfig().get("settings", "search_query")
    hashedHashtag = hashlib.md5(hashtag.encode('ascii')).hexdigest()
    last_id_filename = "last_id_hashtag_%s" % hashedHashtag
    rt_bot_path = os.path.dirname(os.path.abspath(__file__))
    last_id_file = os.path.join(rt_bot_path, last_id_filename)
    
    # create bot
    api = tweepy.API(getAuth())
    
    # retrieve last savepoint if available
    try:
        with open(last_id_file, "r") as file:
            savepoint = file.read()
    except IOError:
        savepoint = ""
        print("No savepoint found. Bot is now searching for results")
    
    
    # your hashtag or search query and tweet language (empty = all languages)
    hashtag = getConfig().get("settings", "search_query")
    tweetLanguage = getConfig().get("settings", "tweet_language")
    
    # search query
    timelineIterator = tweepy.Cursor(api.search, q=hashtag, since_id=savepoint, lang=tweetLanguage).items(getConfig().get("settings", "number_of_rt"))
    
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
        logger.debug("useridstring in whitelist? %s", (useridstring in whitelist))
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
    with open(last_id_file, "w") as file:
        file.write(str(last_tweet_id))
