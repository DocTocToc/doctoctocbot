#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, inspect, io

from bot.twitter import get_api

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# friends file
friendsfile = os.path.join(path, "friends")                                            
print("friends file: %s" % friendsfile)

# bio file
biofile = os.path.join(path, "bio")                                            
print("bio file: %s" % biofile)

with open(friendsfile, 'r') as f:
    friends = [line.rstrip('\n') for line in f]

print("Number of friends: %s" % len(friends))

# create bot
api = get_api()

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