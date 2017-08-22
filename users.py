#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Implement the user model.

Author: Anatole Hanniet.
License: Mozilla Public License (2.0), see 'LICENSE' for details.
"""


from sqlalchemy import BigInteger, Column, String
from database import Base, Session
from tweepy import Cursor
from utils import connect, load_config


class User(Base):
    """A user of the application."""

    __tablename__ = 'users'
    identifier = Column(BigInteger, primary_key=True)
    name = Column(String(length=250), index=True)
    description = Column(String(length=250))

    def __repr__(self):
        """Return a unique string representation of the user."""
        return '<User #{0}: {1}>'.format(self.identifier, self.name)


if __name__ == '__main__':
    # Load the configuration
    config = load_config()

    # Connect to the twitter API
    twitter = connect()

    # Connect to the database
    session = Session()

    # Retrieve contributors from a twitter list
    for member in Cursor(twitter.list_members,
                         owner_id=config.getint('twitter', 'ACCOUNT ID'),
                         slug='docs').items():
        user = User(
            identifier=member.id,
            name=member.name,
            description=member.description)
        session.merge(user)

    session.commit()
