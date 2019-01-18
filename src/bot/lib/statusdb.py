#!/usr/bin/env python

"""
Add tweets to databases.
"""

from datetime import datetime
import requests
import logging

from bot.conf.cfg import getConfig
from bot.lib.datetime import get_datetime, get_datetime_tz
from bot.model.model import Status, session
from sqlalchemy.exc import IntegrityError as AlchemyIntegrityError
from django.db import IntegrityError, transaction


"""
    import os
    import django
    import sys
    sys.path.append('.')
    sys.path.append('django')
    os.environ["DJANGO_SETTINGS_MODULE"] = 'doctocnet.settings'
    django.setup()
"""
from conversation.models import Tweetdj



__author__ = "Jerome Pinguet"
__copyright__ = "Copyright 2017-2018, DocTocTocBot"
#__credits__ = [""]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Jerome Pinguet"
__email__ = "jerome@jerome.cc"
__status__ = "Production"

logger = logging.getLogger(__name__)

class Addstatus:
    def __init__(self, json):
        self.json = json

    def addstatus(self):
        try:
            status = Status(id = self.id(),
                        userid = self.userid(),
                        json = self.json,
                        datetime = get_datetime(self.json))
            session.add(status)
            session.commit()
        except AlchemyIntegrityError as e:
            session.rollback()
            logger.debug('Integrity error: {}'.format(e.args[0]))
        if self.has_image():
            self.add_image()
        return True


    def addtweetdj(self):
        """
        Add status to Django database (table tweetdj).
        MPTT tree node is added to treedj inside the overridden save method of
        Tweetdj class, in the Django model.
        """
        try:
            with transaction.atomic():
                status = Tweetdj.objects.create(
                    statusid = self.id(),
                    userid = self.userid(),
                    json = self.json,
                    created_at = get_datetime_tz(self.json),
                    reply = 0,
                    like = self.like(),
                    retweet = self.retweet(),
                    parentid = self.parentid()
                    )
        except IntegrityError as e:
            logger.debug("Status %s already exists in database: %s" % (self.id, e))
            return False
        logger.debug("function addtweetdj added status %s", status)
        return True

    def userid(self):
        return self.json["user"]["id"]

    def id(self):
        return self.json["id"]

    def reply(self):
        return

    def like(self):
        return self.json["favorite_count"]
  
    def retweet(self):
        return self.json["retweet_count"]

    def has_image(self):
        """ returns True if the status contains at least one image."""
        if "extended_entities" not in self.json:
            return False
        elif self.json["extended_entities"]["media"][0]["type"] == "photo":
            return True
        else:
            return False

    def add_image(self):
        """ Stores one or more images contained in the status.
        """
        for photo in self.json["extended_entities"]["media"]: 
            url = photo["media_url_https"]
            filename = url.rsplit('/', 1)[1]
            filepath = getConfig()["images"]["dir"] + filename
            r = requests.get(url, allow_redirects=True)
            open(filepath, 'wb').write(r.content)

    def parentid(self):
        return self.json["in_reply_to_status_id"]