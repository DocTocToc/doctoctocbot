#!/usr/bin/env python                                                           
# -*- coding: utf-8 -*-                                                         
                                                                                
u"""                                                                            
Bot to enhance french healthcare professionals exchanges on Twitter.            
                                                                                
Author: Jérome Pinguet.                                                         
Based on [retweet-bot](https://github.com/basti2342/retweet-bot) by [Basti](https://github.com/basti2342)
License: Mozilla Public License, see 'LICENSE' for details.                     
"""                                                                             
                                                                                
import argparse
import json
import logging
import os
import tweepy

from conversation.models import Tweetdj

from .lib.statusdb import Addstatus
from .twitter import getAuth
from .twitter import statuses_lookup


logger = logging.getLogger(__name__)

def addstatus(statusid):
    API = tweepy.API(getAuth())
    status = API.get_status(statusid, tweet_mode='extended')
    db = Addstatus(status._json)
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