#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
from bot.twitter import getAuth

def getuser(user_id):
    "get Twitter user object"
    api = tweepy.API(getAuth())
    return api.get_user(id)._json
