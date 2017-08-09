#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Bot to enhance french healthcare professionals exchanges on Twitter.

Tweets are only retweeted if the user wants to use the service of
DocTocTocBot. List of DocTocTocBot subscribers is persist as a Twitter list
(private) of the bot account.

Author: Jérome Pinguet.
License: Mozilla Public License, see 'LICENSE' for details.
"""

from configparser import ConfigParser
from pathlib import Path
import tweepy


botid = 881706502939185152
slug = "docs"

# Determine absolute path to the bot's directory
ROOT_PATH = Path(__file__).resolve().parent

file_ = ROOT_PATH.joinpath("docs")

# read config
config = ConfigParser()
config.read(str(ROOT_PATH.joinpath("config")))

# your hashtag or search query and tweet language (empty = all languages)
tweetLanguage = config.get("settings", "tweet_language")

# create bot
auth = tweepy.OAuthHandler(
    config.get("twitter", "consumer_key"),
    config.get("twitter", "consumer_secret")
    )
auth.set_access_token(
    config.get("twitter", "access_token"),
    config.get("twitter", "access_token_secret")
    )
api = tweepy.API(auth, wait_on_rate_limit=True)

docs = []

# In this example, the handler is time.sleep(15 * 60),
# but you can of course handle it in any way you want.

members = tweepy.Cursor(api.list_members, owner_id=botid, slug='docs').items()
ids = [user.id for user in members]

for id_ in ids:
    docs.append(id_)

with open(file_, mode='wt') as f:
    for id_ in ids:
            f.write(str(id_) + '\n')
