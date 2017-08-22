#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Implement usefull tools for the project.

Author: Anatole Hanniet.
License: Mozilla Public License (2.0), see 'LICENSE' for details.
"""

from configparser import ConfigParser
from pathlib import Path
from tweepy import API, OAuthHandler


ROOT_PATH = Path(__file__).resolve().parent


def load_config(source=ROOT_PATH.joinpath('config.ini')):
    """
    Load a configuration file.

    - source, 'pathlib.Path' object or string representing a path. If not
    provided default location and name are used for the configuration file.
    The default location is the project directory, the default name is
    'config.ini'.

    Return a 'configparser.ConfigParser' instance.
    """
    config = ConfigParser()
    config.read(str(source))
    return config


def connect(source=ROOT_PATH.joinpath('config.ini')):
    """
    Connect to the Twitter API.

    Return a 'tweepy.API' object to access the Twitter API.
    """
    config = load_config()
    auth = OAuthHandler(
        config.get('twitter', 'CONSUMER_KEY'),
        config.get('twitter', 'CONSUMER_SECRET'))
    auth.set_access_token(
        config.get('twitter', 'ACCESS_TOKEN'),
        config.get('twitter', 'ACCESS_TOKEN_SECRET'))
    return API(auth)
