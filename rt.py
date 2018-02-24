#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Bot to enhance french healthcare professionals exchanges on Twitter.

Author: Jérome Pinguet.
License: Mozilla Public License, see 'LICENSE' for details.
"""

import tweepy
import sys
import pprint
import json
from cfg import getConfig, whitelist
from doctoctocbot import getAuth, okrt, isrt, iswhitelist, okblacklist, retweet

print(len(sys.argv))

if len(sys.argv)<2:
    print("empty argument")
    exit(0)

status_filename = sys.argv[1]
f = open(status_filename, "r")
data = f.read()
print("type of data: ")
print(type(data))
print("\n")
pprint.pprint(data)
print("\n")
data_json = json.loads(data)
pprint.pprint(data_json)

print("is it a RT? ", isrt(data_json))
print("is user id in whitelist? ", iswhitelist(data_json))

print("okblacklist? ", okblacklist(data_json))

print("shoud we rt this status? okrt = ", okrt(data_json))
