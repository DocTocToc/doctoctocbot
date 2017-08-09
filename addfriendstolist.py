#!/usr/bin/env python
# -*- coding: utf-8 -*-

# add friends (whitelist) to privat Twitter list "docs"
# bot user_id=881706502939185152

from configparser import ConfigParser
from Pathlib import Path
import tweepy


slug = "docs"
bot_id = 881706502939185152

# Determine absolute path to the bot's directory
ROOT_PATH = Path(__file__).resolve().parent

file_ = ROOT_PATH.joinpath("friends")
print "friends file:", file_

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

with open(file_, mode='r') as f:
    friends = [line.rstrip('\n') for line in f]

lists = api.lists_all()
print "List of the lists \n"
for list_ in lists:
    print "list: ", list_.slug, list_.id

for friend in friends:
    api.add_list_member(owner_id=bot_id, slug=slug, user_id=int(friend))
    print "The user {} was added to list {}.".format(friend, slug)
