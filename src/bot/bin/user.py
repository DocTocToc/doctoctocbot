#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
import logging
from typing import List

from bot.tweepy_api import get_api

logger = logging.getLogger(__name__)

def getuser(user_id: int, bot_screen_name=None):
    "Get one Twitter user object from one user id."
    if not user_id:
        return
    if not isinstance(user_id, int):
        return

    api = get_api(
        username=bot_screen_name,
        backend=True,
    )
    try:
        return api.get_user(user_id)._json
    except AttributeError:
        return

def getuser_lst(user_id_lst: List[int]):
    "Get a list of Twitter user objects from list of user ids."
    if not user_id_lst:
        return
    if not all(isinstance(n, int) for n in user_id_lst):
        return

    api = get_api()
    try:
        users = api.lookup_users(user_id_lst)
    except tweepy.error.TweepError as e:
        logger.error("Tweepy or Twitter API error: %s" % e)
        return
    except AttributeError:
        return 
    return [user._json for user in users]
