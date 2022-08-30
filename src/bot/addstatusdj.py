#!/usr/bin/env python                                                           
# -*- coding: utf-8 -*-                                                         
                                                                                
u"""                                                                            
Bot to enhance french healthcare professionals exchanges on Twitter.            
                                                                                
Author: Jérome Pinguet.                                                         
Based on [retweet-bot](https://github.com/basti2342/retweet-bot) by [Basti](https://github.com/basti2342)
License: Mozilla Public License, see 'LICENSE' for details.                     
"""                                                                             
import argparse
import logging
import tweepy

from conversation.models import Tweetdj

from .lib.statusdb import Addstatus
from bot.tweepy_api import get_api
from bot.tweepy_api import statuses_lookup
from bot.lib.status import api_switch_get_status

logger = logging.getLogger(__name__)

#tweepy.error.TweepError: [{'code': 136, 'message': 'You have been blocked from the author of this tweet.'}]

def addstatus(statusid, bot_username=None):
    API = get_api(username=bot_username)
    try:
        status = API.get_status(statusid, tweet_mode='extended')
    except AttributeError:
        return
    except tweepy.error.TweepError as e:
        logger.error(f"addstatus: Tweepy error: {e}")
        # tweepy.error.TweepError: [{'code': 136, 'message': 'You have been blocked from the author of this tweet.'}]
        if e.args[0][0]['code'] == 136:
            status = api_switch_get_status(
                statusid,
                tweet_mode='extended',
                exclude=bot_username
            )
    try:
        db = Addstatus(status._json)
    except AttributeError:
        if status is None:
            logger.error(f"We could not get status {statusid}")
        return
    db.addtweetdj()

def addstatus_if_not_exist(statusid):
    if statusid is None:
        return
    elif type(statusid) is int:
        sid_lst = [statusid]
    else:
        sid_lst = statusid
    present = list(Tweetdj.objects.filter(statusid__in=sid_lst).values_list('statusid', flat=True))
    absent = list(set(sid_lst)- set(present))
    if not absent:
        return
    absent_statuses = statuses_lookup(absent)
    if not absent_statuses:
        return
    for status in absent_statuses:
        if hasattr(status, '_json'):
            db = Addstatus(status._json)
            db.addtweetdj()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "statusid",
        help="add a tweet with the given statusid to Django database",
        type=int
    )
    args = parser.parse_args()
    statusid = args.statusid
    addstatus(statusid)