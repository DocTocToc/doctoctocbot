#!/usr/bin/env python                                                           
# -*- coding: utf-8 -*-                                                         
                                                                                
u"""                                                                            
Bot to enhance french healthcare professionals exchanges on Twitter.            
                                                                                
Author: Jérome Pinguet.                                                         
Based on [retweet-bot](https://github.com/basti2342/retweet-bot) by [Basti](https://github.com/basti2342)
License: Mozilla Public License, see 'LICENSE' for details.                     
"""                                                                             
                                                                                
import os
import json
import tweepy                                                                   
from twitter import getAuth                                                     
from conf.cfg import getConfig                                                  
from log import setup_logging
import logging
import argparse
from lib.statusdb import Addstatus

setup_logging()                                                                 
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "statusid",
        help="add a tweet with the given statusid to Django database",
        type=int
    )
    args = parser.parse_args()
    statusid = args.statusid
    logger.debug("!!!!!!!!!!!!!!!!!!!!!!!! type(arg): %s", type(statusid)) 
    # create bot                                                                
    API = tweepy.API(getAuth())

    status = API.get_status(statusid)
    db = Addstatus(status._json)
    db.addtweetdj()

