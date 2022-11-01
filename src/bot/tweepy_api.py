#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import tweepy
from itertools import cycle
from tweepy import TweepError
import mytweepy
from mytweepy import TweepyException
import time
import random
from datetime import datetime
from bot.models import Account, AccessToken, TwitterApp, TwitterAPI

from django.conf import settings

from social_django.models import UserSocialAuth
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

def gen_api():
    qs = Account.objects.filter(active=True)
    api_lst = [get_api(account.username) for account in qs]
    for i in cycle(api_lst):
        yield i

def getAuth1(username, mt):
    "get Tweepy OAuthHandler authentication object"
    if username:
        try:
            account = Account.objects.get(username=username)
            logger.debug(f'{account=}')
        except Account.DoesNotExist:
            return getSocialDjangoAuth(username)
        auth = oauth1(account, mt)
    else:
        auth = getRandomAuth1()
    return auth

def getRandomAuth1(mt):
    """Get a status through the account of another community
    Try to get a status through another account if the bot of a community was
    blocked by the author of the status.
    """
    accounts = list(Account.objects.all())
    random.shuffle(accounts)
    for account in accounts:
        auth = oauth1(account, mt)
        if auth:
            return auth

def oauth1(account, mt):
    if mt:
        try:
            auth = mytweepy.OAuthHandler(
                account.twitter_consumer_key,
                account.twitter_consumer_secret
            )
        except TweepyException as e:
            logger.error(e)
            return
        try:
            auth.set_access_token(
                account.twitter_access_token,
                account.twitter_access_token_secret
            )
        except TweepyException as e:
            logger.error(e)
            return
    else:
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

def get_api(username=None, mt=False):
    try:
        account = Account.objects.get(username=username)
    except Account.DoesNotExist:
        return getSocialDjangoAuth(username)
    try:
        v1 = TwitterAPI.objects.get(name="standard v1.1")
        v2 = TwitterAPI.objects.get(name="v2")
    except TwitterAPI.DoesNotExist as e:
        logger.error(f'{e}: create TwitterAPI records. ')
        return
    if account.app.api == v1:
        return get_api_1(username, mt)
    elif account.app.api == v2:
        return get_api_2(username)
    else:
        logger.error(f'{account} is not linked to an app using API v1 or v2. ')
        return

def get_api_2(username):
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
        return mytweepy.Client(access_token, wait_on_rate_limit=True)

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

def get_api_1(username, mt):
    auth = getAuth1(username, mt)
    if not auth:
        return
    if mt:
        try:
            return mytweepy.API(
                auth,
                wait_on_rate_limit=True,
            )
        except TweepyException as e:
            logger.error(e)
    else:
        try:
            return tweepy.API(
                auth,
                wait_on_rate_limit=True,
                wait_on_rate_limit_notify=True
            )
        except tweepy.TweepError as e:
            logger.error(e)



def get_v1_v2():
    try:
        v1 = TwitterAPI.objects.get(name="standard v1.1")
        v2 = TwitterAPI.objects.get(name="v2")
        return v1, v2
    except TwitterAPI.DoesNotExist as e:
        logger.error(f'{e}: create TwitterAPI records. ')
        return None, None