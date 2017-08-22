#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Implement the user model.

Author: Anatole Hanniet.
License: Mozilla Public License (2.0), see 'LICENSE' for details.
"""


from sqlalchemy import BigInteger, Column, String
from database import Base


class User(Base):
    """A user of the application."""

    __tablename__ = 'users'
    identifier = Column(BigInteger, primary_key=True)
    name = Column(String(length=250), index=True)

    def __repr__(self):
        """Return a unique string representation of the user."""
        return '<User #{0}: {1}>'.format(self.identifier, self.name)
