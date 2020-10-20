from django.test import TestCase
import random
import logging
import ast
from datetime import datetime
import pytz

from bot.models import Account
from community.models import Community
from moderation.models import SocialUser, SocialMedia
from conversation.models import Tweetdj
from tagging.models import Queue, Process
from dm.models import DirectMessage
from tagging.tasks import poll_tag_dm

from tagging.tests.constants import STATUS_JSON_RAW

logger = logging.getLogger(__name__)


class TaggingTestCase(TestCase):
    BOT_USERID = random.getrandbits(63)
    BOT_USERNAME = "test_bot"
    COMMUNITY_NAME = "test_community"
    STATUS_ID = random.getrandbits(63)
    STATUS_JSON = ast.literal_eval(STATUS_JSON_RAW)
    DATE_TIME_NOW = datetime.utcnow().replace(tzinfo=pytz.utc)
    CATEGORY = "diagnostic"
    DM_JSON = {
        "text": "#diagnostic",
        "entities": {
            "urls": [],
            "symbols": [],
            "hashtags": [{
                "text": "diagnostic",
                "indices": [0, 11]}],
            "user_mentions": []
        },
        "quick_reply_response": {
            "type": "options",
            "metadata": "category8f437259-f2b9-4c0d-b426-053b550a4ddddiagnostic"
        }
    }
    
    def setUp(self):
        account = Account.objects.create(
            userid = TaggingTestCase.BOT_USERID,
            username = TaggingTestCase.BOT_USERNAME,
        )
        community = Community.objects.create(
            name = TaggingTestCase.COMMUNITY_NAME,
            account=account,
        )
        ## create default SocialMedia
        social_media, _created = SocialMedia.objects.get_or_create(
            name="twitter",    
        )
        ## Create test author SocialUser
        social_user_author = SocialUser.objects.create(
            user_id = random.getrandbits(63),
            social_media = social_media,
        )
        ## Create test processor SocialUser
        social_user_processor = SocialUser.objects.create(
            user_id = random.getrandbits(63),
            social_media = social_media,
        )
        ## Create TweetDj status to tag with given id
        status = Tweetdj.objects.create(
            statusid = TaggingTestCase.STATUS_ID,
            userid = social_user_author.user_id,
            socialuser = social_user_author,
            json = TaggingTestCase.STATUS_JSON,
            created_at = TaggingTestCase.DATE_TIME_NOW
        )
        queue = Queue.objects.create(
            uid = status.statusid,
            socialmedia = social_media,
            community = community,
        )
        process = Process.objects.create(
            queue = queue,
            processor = social_user_processor,    
        )
        # Create answer DM
        metadata = f"category{process.id}{TaggingTestCase.CATEGORY}"
        TaggingTestCase.DM_JSON["quick_reply_response"]["metadata"] = metadata
        _dm = DirectMessage.objects.create(
            id = random.getrandbits(63),
            created_timestamp = datetime.utcnow().timestamp()*1000,
            sender_id = social_user_processor.user_id,
            recipient_id = TaggingTestCase.BOT_USERID,
            text = "#" + TaggingTestCase.CATEGORY,
            jsn = TaggingTestCase.DM_JSON,
        )

    def test_poll_tag_dm(self):
        poll_tag_dm()
        status = Tweetdj.objects.get(statusid = TaggingTestCase.STATUS_ID)
        self.assertEqual(status.tags.all()[0].name, TaggingTestCase.CATEGORY)