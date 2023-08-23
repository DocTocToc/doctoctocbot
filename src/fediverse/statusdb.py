"""
Add toots to database.
"""

import logging
import re
import json
from django.db import IntegrityError, DatabaseError, transaction
from django.conf import settings
from conversation.tasks import handle_image
from moderation.models import MastodonUser, addsocialuser_from_userid
from fediverse.models import Toot
from conversation.models import Hashtag
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers

logger=logging.getLogger(__name__)

class TootDb:
    def __init__(self, status):
        self.status = status
        self.db_id = int(status["id"])

    def add(self, update=False):
        if Toot.objects.filter(db_id=self.db_id).exists() and update:
            return self.update()
        else:
            return self.create()

    def create(self) -> Toot:
        try:
            toot = Toot.objects.create(
                user=self.get_user(),
                uri_id=self.get_uri_id(),
                db_id=self.db_id,
                created_at=self.status.created_at,
                edited_at=self.status.edited_at,
                in_reply_to_id=self.get_in_reply_to_id(),
                in_reply_to_account_id=self.get_in_reply_to_account_id(),
                status=self.get_status()
            )
        except DatabaseError as e:
            logger.error(e)
            return

        toot.hashtag.set(self.get_hashtag())
        return toot

    def update(self):
        pass

    def get_uri_id(self):
        match = re.search("\d*$", self.status["uri"])
        uri_id = str(match.group())
        return int(uri_id)

    def get_user(self):
        acct=self.status["account"]["acct"]
        if not '@' in acct:
            domain = settings.MASTODON_DOMAIN
            if domain:
                acct = f'{acct}@{domain}'
        try:
            return MastodonUser.objects.get(
                acct=acct
            )
        except MastodonUser.DoesNotExist:
            return MastodonUser.objects.create(acct=acct)

    def get_hashtag(self):
        tags = [tag["name"].lower() for tag in self.status["tags"]]
        hashtag = []
        for tag in tags:
            try:
                hashtag.append(
                    Hashtag.objects.get(hashtag=tag)
                )
            except Hashtag.DoesNotExist:
                continue
        return hashtag

    def get_in_reply_to_id(self):
        try:
            return int(self.status["in_reply_to_id"])
        except TypeError:
            return

    def get_in_reply_to_account_id(self):
        try:
            return int(self.status["in_reply_to_account_id"])
        except TypeError:
            return

    def get_status(self):
        return json.loads(
            json.dumps(self.status, cls=DjangoJSONEncoder)
        )
