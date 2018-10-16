#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
from twitter import getAuth
from conf.cfg import getConfig
from log import setup_logging
import logging
import random
import string

setup_logging()
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    hashtag = "#doctoctoctest"
    randomchars = "".join( [random.choice(string.ascii_letters) for i in range(15)] )
    status = hashtag + " " + randomchars
    logger.debug(status)
    api = tweepy.API(getAuth())
    api.update_status(status)
