#!/usr/bin/env python
# -*- coding: utf-8 -*-

# make a list of the bot's friends (whitelist)

import os, configparser, tweepy, inspect, pickle, time

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
api = tweepy.API(auth)

friends = [ ]

# In this example, the handler is time.sleep(15 * 60),
# but you can of course handle it in any way you want.

def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)

for friend_id in api.friends_ids(881706502939185152):
    print friend_id
    friends.append(friend_id) 

with open(file, mode='wt') as f:
    for s in friends:
            f.write(str(s) + '\n')
