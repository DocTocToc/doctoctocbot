#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
import io
from pathlib import Path
import tweepy


path = Path(__file__).resolve().parent

# friends file
friendsfile = path.joinpath("friends")
print "friends file:", friendsfile

# bio file
biofile = path.joinpath("bio")
print "bio file:", biofile

# read config
config = ConfigParser()
config.read(path.joinpath("config"))

# tweet language (empty = all languages)
tweetLanguage = config.get("settings", "tweet_language")


# whitelisted users and words
# eg: ["medecinelibre", "freemedsoft"]
# userWhitelist = ["medecinelibre", "freemedsoft", "LibreHealthCare"]
with open(friendsfile, 'r') as f:
    friends = [line.rstrip('\n') for line in f]

print "Number of friends:", len(friends)

# create bot
auth = tweepy.OAuthHandler(
    config.get("twitter", "consumer_key"),
    config.get("twitter", "consumer_secret")
    )
auth.set_access_token(
    config.get("twitter", "access_token"),
    config.get("twitter", "access_token_secret")
    )
api = tweepy.API(auth)

# API limit to GET users: 100 per call
bio = ""
max = 100
friendschunks = [friends[i:i + max] for i in range(0, len(friends), max)]

for chunk in friendschunks:
    users = api.lookup_users(user_ids=chunk)
    for user in users:
        bio += (user.description + "\n")

print bio
with io.open(biofile, encoding='utf-8', mode='wt') as f:
    f.write(bio)
