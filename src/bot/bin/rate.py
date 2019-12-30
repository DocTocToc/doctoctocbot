#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bot.tweepy_api import get_api

def getratelimit():
    "get Twitter API rate limit info"
    api = get_api()
    return "API rate limite status: {0}".format(api.rate_limit_status())
