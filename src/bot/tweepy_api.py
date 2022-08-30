#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import tweepy
import mytweepy
import time
import random
from datetime import datetime
from bot.models import Account, AccessToken, TwitterApp

from django.conf import settings

from social_django.models import UserSocialAuth
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

def getAuth1(username=None):
    "get Tweepy OAuthHandler authentication object"
    if username:
        try:
            account = Account.objects.get(username=username)
            logger.debug(f'{account=}')
        except Account.DoesNotExist:
            return getSocialDjangoAuth(username)
        auth = oauth1(account)
    else:
        auth = getRandomAuth1()
    return auth

def getRandomAuth1():
    """Get a status through the account of another community
    Try to get a status through another account if the bot of a community was
    blocked by the author of the status.
    """
    accounts = list(Account.objects.all())
    random.shuffle(accounts)
    for account in accounts:
        auth = oauth1(account)
        if auth:
            return auth

def oauth1(account):
    try:
        auth = tweepy.OAuthHandler(
            account.twitter_consumer_key,
            account.twitter_consumer_secret
        )
    except tweepy.TweepError as e:
        logger.error(e)
        return
    try:
        auth.set_access_token(
            account.twitter_access_token,
            account.twitter_access_token_secret
        )
    except tweepy.TweepError as e:
        logger.error(e)
        return
    return auth

def getSocialDjangoAuth(username):
    "get Tweepy OAuthHandler authentication object"
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return getAuth1()
    try:
        user_social_auth = UserSocialAuth.objects.get(user=user)
    except UserSocialAuth.DoesNotExist:
        return getAuth1()
    if (user_social_auth.provider != "twitter"):
        return getAuth1()
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

def get_api(username=None, oauth2=False):
    if oauth2:
        return get_api_2(username=username)
    else:
        return get_api_1(username=username)

def get_api_2(username=None):
    if username:
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist:
            return getSocialDjangoAuth(username)
        try:
            at = AccessToken.objects.get(
                oauth = AccessToken.OAuth.OAUTH2.value,
                account = account,
            )
            logger.debug(f'AccessToken object: {at}')
        except AccessToken.DoesNotExist:
            return
        logger.debug(f'{list(at.app.scopes.all().values_list("scope", flat=True))=}')
        oauth2_user_handler = mytweepy.OAuth2UserHandler(
            client_id=at.app.client_id,
            redirect_uri=at.app.redirect_uri,
            scope=list(at.app.scopes.all().values_list("scope", flat=True)),
            client_secret=at.app.client_secret
        )
        expiry_ts = at.token["expires_at"]
        if (expiry_ts - time.time()) < 3600:
            logger.debug("refresh token")
            access_token_dict = oauth2_user_handler.refresh_token(
                refresh_token=at.token["refresh_token"]
            )
            at.token = access_token_dict
            at.save()
            access_token = access_token_dict["access_token"]
        else:
            access_token = at.token["access_token"]
        return mytweepy.Client(access_token)

def get_oauth2userhandler(app):
    try:
        app = TwitterApp.objects.get(name=app)
        logger.debug(f'{app=}')
    except TwitterApp.DoesNotExist:
        return
    oauth2_user_handler = mytweepy.OAuth2UserHandler(
        client_id=app.client_id,
        redirect_uri=app.redirect_uri,
        scope=list(app.scopes.all().values_list("scope", flat=True)),
        client_secret=app.client_secret
    )
    logger.debug(f'{oauth2_user_handler=}')
    return oauth2_user_handler

def get_oauth2userhandler_authorization_url(app):
    oauth2userhandler = get_oauth2userhandler(app)
    if not oauth2userhandler:
        return
    return oauth2userhandler, oauth2userhandler.get_authorization_url()

def oauth2userhandler_fetch_token(username, oauth2userhandler, url):
    try:
        account = Account.objects.get(username=username)
    except Account.DoesNotExist:
        return
    try:
        app = TwitterApp.objects.get(client_id=oauth2userhandler.client_id)
    except TwitterApp.DoesNotExist:
        return
    access_token_dict = oauth2userhandler.fetch_token(url)
    if (
        not access_token_dict
        or not isinstance(access_token_dict, dict)
        or not access_token_dict.get("access_token", None)
    ):
        logger.warn(f'{access_token_dict=} is not valid')
        return
    access_token, _created = AccessToken.objects.get_or_create(
        oauth=AccessToken.OAuth.OAUTH2.value,
        account=account,
        app=app
    )
    access_token.token = access_token_dict
    access_token.save()

def get_api_1(username=None):
    auth = getAuth1(username)
    if not auth:
        return
    try:
        return tweepy.API(
            auth,
            wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True
        )
    except tweepy.TweepError as e:
        logger.error(e)

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
            s_lst = API.statuses_lookup(
                ids,
                include_entities=True,
                tweet_mode='extended'
            )
        except tweepy.TweepError as e:
            logger.debug("Tweepy error: %s", e)
            continue
        statuses.append(s_lst)
    if len(statuses) > 1:
        return statuses
    elif len(statuses) == 1:
        return statuses[0]