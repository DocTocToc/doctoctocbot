#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
from twitter import getAuth

from cfg import getConfig


def getratelimit():
    "get Twitter API rate limit info"
    api = tweepy.API(getAuth())
    return "API rate limite status: {0}".format(api.rate_limit_status())
