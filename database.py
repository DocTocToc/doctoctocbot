#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Implement the database

Author: Anatole Hanniet.
License: Mozilla Public License (2.0), see 'LICENSE' for details.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils import load_config


# Parent class for every class which objects need to be persist in the
# database.
Base = declarative_base()

# Create a session factory
config = load_config()
engine = create_engine(config.get('DATABASE', 'URL'))
Session = sessionmaker(bind=engine)
