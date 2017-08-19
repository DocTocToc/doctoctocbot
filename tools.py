#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
from tweepy import API, OAuthHandler


def load_configuration(source):
    """Load an INI configuration file."""
    configuration = ConfigParser()
    configuration.read(str(source))
    return configuration


def connect(app_token, app_secret, access_token, access_secret):
    """Connect to the Twitter API."""
    auth = OAuthHandler(app_token, app_secret)
    auth.set_access_token(access_token, access_secret)
    return API(auth)
