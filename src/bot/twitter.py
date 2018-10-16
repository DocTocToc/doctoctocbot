#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
from .conf.cfg import getConfig

def getAuth( ):
    "get Tweepy OAuthHandler authentication object"
    config = getConfig()
    auth = tweepy.OAuthHandler(config["twitter"]["consumer_key"], config["twitter"]["consumer_secret"])
    auth.set_access_token(config["twitter"]["access_token"], config["twitter"]["access_token_secret"])
    return auth
