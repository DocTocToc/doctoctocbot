#!/usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Implement model and storage for bot's contributors.

Author: Anatole Hanniet.
License: Mozilla Public License (2.0), see 'LICENSE' for details.
"""

from sqlalchemy import Column
from sqlalchemy import Integer, String
from database import Base


class User(Base):
    """A user of the service."""

    __tablename__ = 'user'
    identifier = Column(Integer, primary_key=True)
    name = Column(String(length=250), nullable=True, unique=True, index=True)

    def __repr__(self):
        """Create a unique text representation of the user."""
        return '<User #{0}: {1}>'.format(self.identifier, self.name)
