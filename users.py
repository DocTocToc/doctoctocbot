#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Implement model and storage for bot's contributors.

Author: Anatole Hanniet.
License: Mozilla Public License (2.0), see 'LICENSE' for details.
"""

from pathlib import Path
from sqlalchemy import Column
from sqlalchemy import Integer, String
from tweepy import Cursor
from database import Base, Session
from tools import connect, load_configuration


class User(Base):
    """A user of the service."""

    __tablename__ = 'user'
    identifier = Column(Integer, primary_key=True)
    name = Column(String(length=250), nullable=True, unique=True, index=True)

    def __repr__(self):
        """Create a unique text representation of the user."""
        return '<User #{0}: {1}>'.format(self.identifier, self.name)


if __name__ == '__main__':
    # Finding the configuration file.
    root = Path(__file__).resolve().parent
    configuration = load_configuration(root.joinpath('configuration.txt'))

    # Authenticating to the Twitter API
    twitter = connect(
        app_token=configuration.get('API ACCESS', 'APP TOKEN'),
        app_secret=configuration.get('API ACCESS', 'APP SECRET'),
        access_token=configuration.get('API ACCESS', 'ACCESS TOKEN'),
        access_secret=configuration.get('API ACCESS', 'ACCESS SECRET')
    )

    # Connecting to the database
    session = Session()

    # Downloading users.
    for user in Cursor(twitter.list_members,
                       owner_id=configuration.get('GLOBAL', 'ACCOUNT ID'),
                       slug='docs').items():
        u = User(identifier=user.id, name=user.name)
        session.merge(u)

    session.commit()
    session.close()
