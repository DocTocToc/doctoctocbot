#!/usr/bin/env python

"""
Add tweets to databases.
"""

import logging

from bot.lib.datetime import get_datetime_tz
from django.db import IntegrityError, DatabaseError, transaction
from django.conf import settings
from conversation.retweet import add_retweeted_by, add_quoted_by
from conversation.tasks import handle_image
from moderation.models import addsocialuser_from_userid
from conversation.models import Tweetdj, Hashtag
from conversation.search.search_vector import TextSearchVector
from common.utils import dictextract


__author__ = "Jerome Pinguet"
__copyright__ = "Copyright 2017-2019, DocTocTocBot"
#__credits__ = [""]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Jerome Pinguet"
__email__ = "jerome@jerome.cc"
__status__ = "Production"

logger = logging.getLogger(__name__)


def add_status_text(tweetdj):
    tsv=TextSearchVector(tweetdj)
    tsv.update_status_text()


class Addstatus:
    def __init__(self, json):
        self.json = json
        self.statusid = json["id"]

    def addtweetdj(self, update=False):
        """
        Add status to Django database (table tweetdj).
        MPTT tree node is added to treedj inside the overridden save method of
        Tweetdj class, in the Django model.
        """
        if Tweetdj.objects.filter(statusid=self.statusid).exists() and update:
            return self.update()
        else:
            return self.create()

    def create(self):
        try:
            with transaction.atomic():
                self.tweetdj = Tweetdj.objects.create(
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
                    deleted = None,
                )
            logger.debug(f"function addtweetdj added status {self.tweetdj}")
        except IntegrityError:
            logger.warn(
                f"Status {self.statusid} already exists in database."
            )
            try:
                return Tweetdj.objects.get(statusid=self.statusid), False
            except Tweetdj.DoesNotExist:
                return None, False
        except DatabaseError:
            return None, False
        self.hashtag_m2m()
        if self.tweetdj.retweetedstatus:
            add_retweeted_by(
                statusid = self.json["retweeted_status"]["id"],
                userid = self.json["retweeted_status"]["user"]["id"],
                by_socialuserid = self.tweetdj.socialuser.id
            )
        elif self.tweetdj.quotedstatus:
            add_quoted_by(
                statusid = self.json["quoted_status"]["id"],
                userid = self.json["quoted_status"]["user"]["id"],
                by_socialuserid = self.tweetdj.socialuser.id
            )
        if not self.tweetdj.retweetedstatus:
            add_status_text(self.tweetdj)
        return self.tweetdj, True

    def update(self):
        """
        Update some fields of an existing Tweetdj object.
        """
        with transaction.atomic():
            try:
                self.tweetdj = Tweetdj.objects.get(pk=self.statusid)
            except Tweetdj.DoesNotExist:
                return None, False
            self.tweetdj.json = self.json
            self.tweetdj.socialuser = addsocialuser_from_userid(self.userid())
            self.tweetdj.created_at = get_datetime_tz(self.json)
            self.tweetdj.like = self.like()
            self.tweetdj.retweet = self.retweet()
            self.tweetdj.parentid = self.parentid()
            self.tweetdj.quotedstatus = self.has_quoted_status()
            self.tweetdj.retweetedstatus = self.has_retweeted_status()
            self.tweetdj.save()
            self.hashtag_m2m()
        logger.debug(f"updated tweetdj {self.tweetdj}")
        return self.tweetdj, False

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

    def hashtag_m2m(self):
        jsn = self.json
        key = "hashtags"
        keyword_lst = Hashtag.objects.values_list("hashtag", flat=True)
        if not keyword_lst:
            return
        keyword_lst_lower = [keyword.lower() for keyword in keyword_lst]
        hash_dct = dict()
        for h in Hashtag.objects.all():
            hash_dct[h.hashtag.lower()]= h
        hashtag_mi_lst = []
        for hashtags in dictextract(key, jsn):
            for hashtag in hashtags:
                status_hashtag = hashtag["text"].lower()
                if status_hashtag in keyword_lst_lower:
                    hashtag_mi = hash_dct[status_hashtag]
                    hashtag_mi_lst.append(hashtag_mi)
        for h in hashtag_mi_lst:
            try:
                self.tweetdj.hashtag.add(h)
            except DatabaseError as e:
                logger.error(e)
                continue