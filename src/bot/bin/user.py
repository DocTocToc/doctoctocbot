#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
import logging
from typing import List
from bot.tweepy_api import get_api
from bot.models import Account
from bot.account import random_bot_username
logger = logging.getLogger(__name__)

def getuser(user_id: int, bot_screen_name=None):
    "Get one Twitter user object from one user id."
    if not user_id:
        return
    if not isinstance(user_id, int):
        return
    api = get_api(username=bot_screen_name)
    if not api:
        return
    res = None
    try:
        res = api.get_user(user_id=user_id)
    except tweepy.TweepError as error:
        logger.error(f"{error=} {res=}")
        return
    if res:
        try:
            return res._json
        except AttributeError as error:
            logging.error(error)
        except Exception as exception:
            logging.error(exception)

def getuser_lst(user_id_lst: List[int]):
    "Get a list of Twitter user objects from list of user ids."
    if not user_id_lst:
        return
    if not all(isinstance(n, int) for n in user_id_lst):
        return
    username = random_bot_username()
    try:
        api = get_api(username=username)
    except TypeError as e:
        logger.error(f'{username=} {e}')
        return
    try:
        users = api.lookup_users(user_id_lst)
    except tweepy.error.TweepError as e:
        logger.error("Tweepy or Twitter API error: %s" % e)
        return
    except AttributeError:
        return 
    return [user._json for user in users]