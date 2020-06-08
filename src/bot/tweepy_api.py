#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import tweepy
from bot.models import Account

from django.conf import settings

from social_django.models import UserSocialAuth
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

def getAuth(username=None, backend=False):
    "get Tweepy OAuthHandler authentication object"
    if username:
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return getSocialDjangoAuth(username)
        if backend:
            auth = tweepy.OAuthHandler(
                account.backend_twitter_consumer_key,
                account.backend_twitter_consumer_secret
            )
            auth.set_access_token(
                account.backend_twitter_access_token,
                account.backend_twitter_access_token_secret
            )
        else:
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

def getSocialDjangoAuth(username):
    "get Tweepy OAuthHandler authentication object"
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return getAuth()
    try:
        user_social_auth = UserSocialAuth.objects.get(user=user)
    except UserSocialAuth.DoesNotExist:
        return getAuth()
    if (user_social_auth.provider != "twitter"):
        return getAuth() 
    auth = tweepy.OAuthHandler(
        settings.SOCIAL_AUTH_TWITTER_KEY,
        settings.SOCIAL_AUTH_TWITTER_SECRET
    )
    logger.debug(user_social_auth.extra_data["access_token"]["oauth_token"])
    logger.debug(user_social_auth.extra_data["access_token"]["oauth_token_secret"])
    auth.set_access_token(
        user_social_auth.extra_data["access_token"]["oauth_token"],
        user_social_auth.extra_data["access_token"]["oauth_token_secret"],
    )
    return auth

def get_api(username=None, backend=False):
    api = tweepy.API(getAuth(username, backend), wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    #verify_credentials(api, username, backend)
    try:
        api.verify_credentials()
    except tweepy.TweepError as e:
        logger.error("Error creating API with Tweepy: {e}")
        return
    return api

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
    
def verify_credentials(api, username, backend):
    try:
        r = api.verify_credentials()
        logger.info(f"Authentication info for {username} (backend: {backend}): {r}")
    except:
        logger.error(f"Error during authentication of {username} (backend: {backend})")