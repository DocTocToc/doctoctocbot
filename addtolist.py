#!/usr/bin/env python
# -*- coding: utf-8 -*-

# add friends (whitelist) to privat Twitter list "docs"
import os, configparser, tweepy, inspect, time

slug = "docs"
bot_id=881706502939185152

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
file = os.path.join(path, "friends")
print "friends file:", file

# read config
config = configparser.SafeConfigParser()
config.read(os.path.join(path, "config"))

# your hashtag or search query and tweet language (empty = all languages)
tweetLanguage = config.get("settings", "tweet_language")

# create bot
auth = tweepy.OAuthHandler(config.get("twitter", "consumer_key"), config.get("twitter", "consumer_secret"))
auth.set_access_token(config.get("twitter", "access_token"), config.get("twitter", "access_token_secret"))
api = tweepy.API(auth, wait_on_rate_limit=True)

with open(file, mode='r') as f:
    friends = [line.rstrip('\n') for line in f]

lists = api.lists_all()
print "List of the lists \n"
for l in lists:
    print "list: ", l.slug, l.id

for friend in friends:
    api.add_list_member(owner_id=bot_id, slug=slug, user_id=int(friend))
    print "The user {} was added to list {}.".format(friend,slug)