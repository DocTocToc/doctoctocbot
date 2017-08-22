#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Implement usefull tools for the project.

Author: Anatole Hanniet.
License: Mozilla Public License (2.0), see 'LICENSE' for details.
"""

from configparser import ConfigParser
from pathlib import Path


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
