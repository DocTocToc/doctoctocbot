#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser


def load_configuration(source):
    """Load an INI configuration file."""
    configuration = ConfigParser()
    configuration.read(str(source))
    return configuration
