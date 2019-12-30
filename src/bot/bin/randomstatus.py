#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random
import string
from bot.tweepy_api import get_api

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    hashtag = "#doctoctoctest"
    randomchars = "".join( [random.choice(string.ascii_letters) for i in range(15)] )
    status = hashtag + " " + randomchars
    logger.debug(status)
    api = get_api()
    api.update_status(status)
