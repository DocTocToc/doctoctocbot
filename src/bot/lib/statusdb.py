#!/usr/bin/env python

"""
Add tweets to databases.
"""

import logging

from bot.lib.datetime import get_datetime_tz
from django.db import IntegrityError, DatabaseError, transaction
from django.conf import settings
from bot.tasks import handle_image
from moderation.models import addsocialuser_from_userid
from conversation.utils import hashtag_m2m_tweetdj
from conversation.models import Tweetdj



__author__ = "Jerome Pinguet"
__copyright__ = "Copyright 2017-2019, DocTocTocBot"
#__credits__ = [""]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Jerome Pinguet"
__email__ = "jerome@jerome.cc"
__status__ = "Production"

logger = logging.getLogger(__name__)

def isrt(status):
    "is this status a RT?"
    isrt = "retweeted_status" in status.keys()
    logger.debug("is this status a retweet? %s" , isrt)
    return isrt

class Addstatus:
    def __init__(self, json):
        self.json = json

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
                    socialuser = addsocialuser_from_userid(self.userid()),
                    json = self.json,
                    created_at = get_datetime_tz(self.json),
                    reply = None,
                    like = self.like(),
                    retweet = self.retweet(),
                    parentid = self.parentid(),
                    quotedstatus = self.json['is_quote_status'],
                    retweetedstatus = isrt(self.json),
                    deleted = None
                )
        except IntegrityError as e:
            logger.warn("Status %s already exists in database: %s" % (self.id, e))
            return False
        logger.debug("function addtweetdj added status %s", status)
        try:
            hashtag_m2m_tweetdj(status)
        except DatabaseError as e:
            logger.error("database error %s", e)
            return False
        logger.debug("added m2m hashtag relationship to %s", status)
        return True

    def userid(self):
        return self.json["user"]["id"]

    def id(self):
        return self.json["id"]

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
        if self.has_image():
            for photo in self.json["extended_entities"]["media"]: 
                url = photo["media_url_https"]
                filename = url.rsplit('/', 1)[1]
                filepath = settings.BOT_IMAGES_PATH + "/" + filename
                handle_image.apply_async(args=(url, filepath), ignore_result=True)

    def parentid(self):
        return self.json["in_reply_to_status_id"]