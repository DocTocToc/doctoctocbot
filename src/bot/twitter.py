#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import tweepy
from bot.models import Account

from django.conf import settings

logger = logging.getLogger(__name__)

def getAuth(username=None):
    "get Tweepy OAuthHandler authentication object"
    if username:
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return getAuth()
        auth = tweepy.OAuthHandler(
            account.twitter_consumer_key,
            account.twitter_consumer_secret
        )
        auth.set_access_token(
            account.twitter_access_token,
            account.twitter_access_token_secret
        )
    else:
        auth = tweepy.OAuthHandler(
            settings.TWITTER_CONSUMER_KEY,
            settings.TWITTER_CONSUMER_SECRET
        )
        auth.set_access_token(
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET
        )
    return auth

def get_api(username=None):
    return tweepy.API(getAuth(username), wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

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