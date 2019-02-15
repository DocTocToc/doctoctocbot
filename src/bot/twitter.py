#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import tweepy

from .conf.cfg import getConfig


logger = logging.getLogger(__name__)

def getAuth():
    "get Tweepy OAuthHandler authentication object"
    config = getConfig()
    auth = tweepy.OAuthHandler(config["twitter"]["consumer_key"], config["twitter"]["consumer_secret"])
    auth.set_access_token(config["twitter"]["access_token"], config["twitter"]["access_token_secret"])
    return auth

def get_api():
    return tweepy.API(getAuth())

def statuses_lookup(statusid):
    """Return a Tweepy Status object or a list of Tweepy Status objects.
    
    statusid -- int or List of int representing the statusid of the tweet object
    """
    if statusid is None:
        return
    elif type(statusid) is int:
        sid_lst = [statusid]
    else:
        sid_lst = statusid
    statuses = []
    size = len(sid_lst)
    while size > 0:
        ids = sid_lst[:100]
        del sid_lst[:100]
        size -= 100
        API = get_api()
        try:
            s_lst = API.statuses_lookup(ids, include_entities=True, tweet_mode='extended')
        except tweepy.TweepError as e:
            logger.debug("Tweepy error: %s", e)
            continue
        statuses.append(s_lst)
    if len(statuses) > 1:
        return statuses
    elif len(statuses) == 1:
        return statuses[0]