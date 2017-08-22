#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Bot to enhance french healthcare professionals exchanges on Twitter.

Author: Jérome Pinguet.
License: Mozilla Public License, see 'LICENSE' for details.
"""

import configparser
import hashlib
import inspect
import os
import tweepy


path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# docs file containing a list of MD id
docsfile = os.path.join(path, "docs")

# read config
config = configparser.SafeConfigParser()
config.read(os.path.join(path, "config"))

# your hashtag or search query and tweet language (empty = all languages)
hashtag = config.get("settings", "search_query")
tweetLanguage = config.get("settings", "tweet_language")

# Number retweets per time
num = int(config.get("settings", "number_of_rt"))
print('Number of retweets:', num)

# whitelisted users and words
# eg: ["medecinelibre", "freemedsoft"]
# userWhitelist = ["medecinelibre", "freemedsoft", "LibreHealthCare"]
with open(docsfile, 'r') as f:
    userIdWhiteList = [line.rstrip('\n') for line in f]

print('Number of users in white list:', len(userIdWhiteList))


# build savepoint path + file
hashedHashtag = hashlib.md5(hashtag.encode('ascii')).hexdigest()
last_id_filename = "last_id_hashtag_%s" % hashedHashtag
rt_bot_path = os.path.dirname(os.path.abspath(__file__))
last_id_file = os.path.join(rt_bot_path, last_id_filename)

# create bot
auth = tweepy.OAuthHandler(config.get("twitter", "consumer_key"), config.get("twitter", "consumer_secret"))
auth.set_access_token(config.get("twitter", "access_token"), config.get("twitter", "access_token_secret"))
api = tweepy.API(auth)

# retrieve last savepoint if available
try:
    with open(last_id_file, "r") as file:
        savepoint = file.read()
except IOError:
    savepoint = ""
    print('No savepoint found. Bot is now searching for results')

# search query
timelineIterator = tweepy.Cursor(api.search, q=hashtag, since_id=savepoint, lang=tweetLanguage).items(num)

# put everything into a list to be able to sort/filter

oklist = []
isRetweet = False

for tweet in timelineIterator:
    isRetweet = False
    user = tweet.user
    screenname = user.screen_name
    userid = user.id
    useridstring = str(userid)
    print('userid:', userid)
    print('useridstring:', useridstring)
    print('screen name:', screenname)
    print('Is user in whitelist:', (useridstring in userIdWhiteList))
    if hasattr(tweet, 'retweeted_status'):
        isRetweet = True
        print('Is retweet:', isRetweet)
    print('text:', tweet.text.encode('utf-8'))
    print('Is user in whitelist:', (useridstring in userIdWhiteList))
    print('Is retweet:', isRetweet)
    if ((useridstring in userIdWhiteList) and (not isRetweet)):
        oklist.append(tweet)
        print('Tweet will be retweeted')
    else:
        print('Tweet will not be retweeted')


try:
    last_tweet_id = oklist[0].id
except IndexError:
    last_tweet_id = savepoint

# filter @replies/blacklisted words & users out and reverse timeline
# remove all tweets with an @mention
# oklist = filter(lambda status: status.text[0] == "@", oklist)

# timeline = filter(lambda status: not any(word in status.text.split() for word in wordBlacklist), timeline)

# timeline = filter(lambda status: status.author.id_str in userIdWhiteList, oklist)
oklist = list(oklist)
oklist.reverse()

tw_counter = 0
err_counter = 0

# iterate the timeline and retweet
for status in oklist:
    try:
        print('{0} {1} {2}'.format(
            status.created_at,
            status.author.screen_name.encode('utf-8'),
            status.text.encode('utf-8')))

        # api.retweet(status.id)
        tw_counter += 1
    except tweepy.error.TweepError as e:
        # just in case tweet got deleted in the meantime or already retweeted
        err_counter += 1
        # print e
        continue

print('Finished.', tw_counter, 'tweets retweeted.', err_counter, 'errors occured.')

# write last retweeted tweet id to file
with open(last_id_file, "w") as file:
    file.write(str(last_tweet_id))
