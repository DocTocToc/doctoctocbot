#!/usr/bin/env python
# -*- coding: utf-8 -*-

# make a list of the bot's friends (whitelist)

import os, tweepy, inspect
from twitter import getAuth
from conf.cfg import getConfig

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

config = getConfig()

whitelistfilename = config['whitelist']['file']
whitelistfilepath = os.path.join(path, whitelistfilename)

slugs = config['whitelist']['slugs']
bot_id = config['settings']['bot_id']

# create bot
auth = getAuth()
api = tweepy.API(auth, wait_on_rate_limit=True)

whitelist = [ ]

for slug in slugs:
    members = tweepy.Cursor(api.list_members, owner_id=bot_id, slug=slug).items()
    ids = [user.id for user in members]
    whitelist.extend(ids)

with open(whitelistfilepath, mode='wt') as f:
    for user_id in whitelist:
            f.write(str(user_id) + '\n')
