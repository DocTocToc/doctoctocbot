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



class Addstatus:
    def __init__(self, json):
        self.json = json
        self.statusid = json["id"]

    def addtweetdj(self):
        """
        Add status to Django database (table tweetdj).
        MPTT tree node is added to treedj inside the overridden save method of
        Tweetdj class, in the Django model.
        """
        try:
            status = Tweetdj.objects.get(pk=self.statusid)
        except Tweetdj.DoesNotExist:
            try:
                with transaction.atomic():
                    status = Tweetdj.objects.create(
                        statusid = self.statusid,
                        userid = self.userid(),
                        socialuser = addsocialuser_from_userid(self.userid()),
                        json = self.json,
                        created_at = get_datetime_tz(self.json),
                        #reply = self.reply(),
                        like = self.like(),
                        retweet = self.retweet(),
                        parentid = self.parentid(),
                        quotedstatus = self.has_quoted_status(),
                        retweetedstatus = self.has_retweeted_status(),
                        deleted = None
                    )
                logger.debug(f"function addtweetdj added status {status}")
            except IntegrityError:
                logger.warn(
                    f"Status {self.statusid} already exists in database."
                )
                return False
            try:
                hashtag_m2m_tweetdj(status)
            except DatabaseError as e:
                logger.error("database error %s", e)
                return False
            logger.debug("added m2m hashtag relationship to %s", status)
            return True

    def updatetweetdj(self):
        """
        Update some fields of an existing Tweetdj object.
        """
        try:
            status = Tweetdj.objects.get(pk=self.statusid)
        except Tweetdj.DoesNotExist:
            return
        with transaction.atomic():
            status.like = self.like(),
            status.retweet = self.retweet(),
            status.save()
        logger.debug(f"updated tweetdj {status}")

    def userid(self):
        return self.json["user"]["id"]

    def like(self):
        return self.json.get("favorite_count")

    def reply(self):
        #That field is only offered in the premium and enterprise API tiers
        return self.json["reply_count"]

    def retweet(self):
        return self.json.get("retweet_count")

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
                handle_image.apply_async(args=(url, filename), ignore_result=True)

    def parentid(self):
        return self.json["in_reply_to_status_id"]

    def has_retweeted_status(self):
        """is this status a RT?
        """
        return "retweeted_status" in self.json.keys()

    def has_quoted_status(self):
        """is this status a Quote?
        """
        return "quoted_status" in self.json.keys()