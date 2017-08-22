#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, configparser, tweepy, inspect, codecs, io

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# friends file
friendsfile = os.path.join(path, "friends")
print("Friends file:", friendsfile)

# bio file
biofile = os.path.join(path, "bio")
print("Bio file:", biofile)

# read config
config = configparser.SafeConfigParser()
config.read(os.path.join(path, "config"))

# tweet language (empty = all languages)
tweetLanguage = config.get("settings", "tweet_language")


# whitelisted users and words
# eg: ["medecinelibre", "freemedsoft"]
#userWhitelist = ["medecinelibre", "freemedsoft", "LibreHealthCare"]
with open(friendsfile, 'r') as f:
    friends = [line.rstrip('\n') for line in f]

print("Number of friends:", len(friends))

# create bot
auth = tweepy.OAuthHandler(config.get("twitter", "consumer_key"), config.get("twitter", "consumer_secret"))
auth.set_access_token(config.get("twitter", "access_token"), config.get("twitter", "access_token_secret"))
api = tweepy.API(auth)

# API limit to GET users: 100 per call
bio = ""
max = 100
friendschunks = [friends[i:i + max] for i in range(0, len(friends), max)]

for chunk in friendschunks:
    users = api.lookup_users(user_ids=chunk)
    for user in users:
        bio+=(user.description + "\n")

print(bio)
with io.open(biofile, encoding='utf-8', mode='wt') as f:
    f.write(bio)
