#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, configparser, tweepy, inspect, io

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# friends file
friendsfile = os.path.join(path, "friends")                                            
print "friends file:", friendsfile

# bio file
biofile = os.path.join(path, "bio")                                            
print "bio file:", biofile 

# read config
config = configparser.SafeConfigParser()
config.read(os.path.join(path, "config"))

# tweet language (empty = all languages)
tweetLanguage = config.get("settings", "tweet_language")


# authorized users and words
# eg: ["medecinelibre", "freemedsoft"]
#userauthorizedlist = ["medecinelibre", "freemedsoft", "LibreHealthCare"]
with open(friendsfile, 'r') as f:
    friends = [line.rstrip('\n') for line in f]

print "Number of friends:", len(friends)

# create bot
auth = tweepy.OAuthHandler(config.get("twitter", "consumer_key"), config.get("twitter", "consumer_secret"))
auth.set_access_token(config.get("twitter", "access_token"), config.get("twitter", "access_token_secret"))
api = tweepy.API(auth)

# API limit to GET users: 100 per call
bio = ""
maximum = 100
friendschunks = [friends[i:i + max] for i in range(0, len(friends), maximum)]

for chunk in friendschunks:
    users = api.lookup_users(user_ids=chunk)
    for user in users:
        bio+=(user.description + "\n")

print bio
with io.open(biofile, encoding='utf-8', mode='wt') as f:
    f.write(bio)
