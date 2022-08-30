import random
import string
import logging
import json
from django.test import TestCase, override_settings

from community.models import Community
from bot.models import Account
from moderation.models import Follower, SocialUser, SocialMedia, Profile
from bot.doctoctocbot import is_follower

logger = logging.getLogger(__name__)

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


class IsFollowerTestCase(TestCase):
    def setUp(self):
        SocialUser.objects.all().delete()
        sm, _ = SocialMedia.objects.get_or_create(name="twitter")
        for user_id in range(1,4):
            su = SocialUser.objects.filter(user_id=user_id)
            if su:
                su.delete()
            su = SocialUser.objects.create(
                user_id=user_id,
                social_media=sm,
            )
            #self.assertEqual(f"su{user_id}: {su}", 0)
            logger.debug(f"su{user_id}: {su}")
        username1 = "username1"
        username2 = "username2"
        bot1, _ = SocialUser.objects.get_or_create(user_id=1, social_media=sm)
        bot2, _ = SocialUser.objects.get_or_create(user_id=2, social_media=sm)
        Profile.objects.create(
            socialuser = bot1,
            json={'screen_name': 'username1'}
        )
        Profile.objects.create(
            socialuser = bot2,
            json={'screen_name': 'username2'}
        )
        account1 = Account.objects.create(
            userid = 1,
            username = username1,
            twitter_consumer_key = get_random_string(100),
            twitter_consumer_secret = get_random_string(100),
            twitter_access_token = get_random_string(100),
            twitter_access_token_secret = get_random_string(100),
            active = True,    
        )
        account2 = Account.objects.create(
            userid = 2,
            username = username2,
            twitter_consumer_key = get_random_string(100),
            twitter_consumer_secret = get_random_string(100),
            twitter_access_token = get_random_string(100),
            twitter_access_token_secret = get_random_string(100),
            active = True,     
        )
        Community.objects.create(
            name = "community1",
            active = True,
            account = account1,
        )
        Community.objects.create(
            name = "community2",
            active = True,
            account = account2,
        )

    @override_settings(UPDATE_SOCIAL_IDS_FORCE_CACHE=True)
    def test_is_follower(self):
        sm, _ = SocialMedia.objects.get_or_create(name="twitter")
        su, _ = SocialUser.objects.get_or_create(user_id=3, social_media=sm)
        bot1, _ = SocialUser.objects.get_or_create(user_id=1, social_media=sm)
        bot2, _ = SocialUser.objects.get_or_create(user_id=2, social_media=sm)
        account1 = Account.objects.get(username="username1")
        account2 = Account.objects.get(username="username2")
        community1 = account1.community
        community2 = account2.community
        logger.debug(
            f'type of {bot1} profile json field: {type(bot1.profile.json)})'
            #f'type of {bot1} profile json field (json.loads): {type(json.loads(bot1.profile.json))})'
            f'value of {bot1} profile json field: {bot1.profile.json})'    
        )
        """
        su is not following any account
        (account1 is NOT among follower_common_account of account2)
        (account2 is NOT among follower_common_account of account1)
        is_follower(su.user_id, username1) should be False
        AND
        is_follower(su.user_id, username2) should be False
        """
        community1.follower_common_account.clear()
        community2.follower_common_account.clear()
        Follower.objects.all().delete()
        Follower.objects.create(
            user = bot1,
            id_list = [],
        )
        Follower.objects.create(
            user = bot2,
            id_list = [],
        )
        self.assertEqual(
            is_follower(su.user_id, bot1.profile.json["screen_name"]),
            False
        )
        self.assertEqual(
            is_follower(su.user_id, bot2.profile.json["screen_name"]),
            False
        )
        """
        su is following account1 of community 1
        su is NOT following account2 of community 2
        (account1 is NOT among follower_common_account of account2)
        (account2 is NOT among follower_common_account of account1)
        is_follower(su.user_id, username1) should be True
        is_follower(su.user_id, username2) should be False
        """
        community1.follower_common_account.clear()
        community2.follower_common_account.clear()
        Follower.objects.all().delete()
        Follower.objects.create(
            user = bot1,
            id_list = [su.user_id],
        )
        Follower.objects.create(
            user = bot2,
            id_list = [],
        )
        self.assertEqual(
            is_follower(su.user_id, bot1.profile.json["screen_name"]),
            True
        )
        self.assertEqual(
            is_follower(su.user_id, bot2.profile.json["screen_name"]),
            False
        )
        """
        su is following account1 of community 1
        su is following account2 of community 2
        account1 is NOT among follower_common_account of account2
        account2 is NOT among follower_common_account of account1
        is_follower(su.user_id, username1) should be True
        is_follower(su.user_id, username2) should be True
        """
        community1.follower_common_account.clear()
        community2.follower_common_account.clear()
        Follower.objects.all().delete()
        Follower.objects.create(
            user = bot1,
            id_list = [su.user_id],
        )
        Follower.objects.create(
            user = bot2,
            id_list = [su.user_id],
        )
        self.assertEqual(
            is_follower(su.user_id, bot1.profile.json["screen_name"]),
            True
        )
        self.assertEqual(
            is_follower(su.user_id, bot2.profile.json["screen_name"]),
            True
        )
        """
        su is not following any account
        (account1 is among follower_common_account of account2)
        (account2 is NOT among follower_common_account of account1)
        is_follower(su.user_id, username1) should be False
        AND
        is_follower(su.user_id, username2) should be False
        """
        community1.follower_common_account.clear()
        community2.follower_common_account.clear()
        community2.follower_common_account.add(account1)
        Follower.objects.all().delete()
        Follower.objects.create(
            user = bot1,
            id_list = [],
        )
        Follower.objects.create(
            user = bot2,
            id_list = [],
        )
        self.assertEqual(
            is_follower(su.user_id, bot1.profile.json["screen_name"]),
            False
        )
        self.assertEqual(
            is_follower(su.user_id, bot2.profile.json["screen_name"]),
            False
        )
        """
        su is following account1 of community 1
        su is NOT following account2 of community 2
        (account1 is among follower_common_account of account2)
        (account2 is NOT among follower_common_account of account1)
        is_follower(su.user_id, username1) should be True
        is_follower(su.user_id, username2) should be True
        """
        community1.follower_common_account.clear()
        community2.follower_common_account.clear()
        community2.follower_common_account.add(account1)
        Follower.objects.all().delete()
        Follower.objects.create(
            user = bot1,
            id_list = [su.user_id],
        )
        Follower.objects.create(
            user = bot2,
            id_list = [],
        )
        self.assertEqual(
            is_follower(su.user_id, bot1.profile.json["screen_name"]),
            True
        )
        self.assertEqual(
            is_follower(su.user_id, bot2.profile.json["screen_name"]),
            True
        )
        """
        su is following account1 of community 1
        su is NOT following account2 of community 2
        (account1 is NOT among follower_common_account of account2)
        (account2 is among follower_common_account of account1)
        is_follower(su.user_id, username1) should be True
        is_follower(su.user_id, username2) should be False
        """
        community1.follower_common_account.clear()
        community2.follower_common_account.clear()
        community1.follower_common_account.add(account2)
        Follower.objects.all().delete()
        Follower.objects.create(
            user = bot1,
            id_list = [su.user_id],
        )
        Follower.objects.create(
            user = bot2,
            id_list = [],
        )
        self.assertEqual(
            is_follower(su.user_id, bot1.profile.json["screen_name"]),
            True
        )
        self.assertEqual(
            is_follower(su.user_id, bot2.profile.json["screen_name"]),
            False
        )
        """
        su is not following any account
        (account1 is among follower_common_account of account2)
        (account2 is among follower_common_account of account1)
        is_follower(su.user_id, username1) should be False
        AND
        is_follower(su.user_id, username2) should be False
        """
        community1.follower_common_account.clear()
        community2.follower_common_account.clear()
        community1.follower_common_account.add(account2)
        community2.follower_common_account.add(account1)
        Follower.objects.all().delete()
        Follower.objects.create(
            user = bot1,
            id_list = [],
        )
        Follower.objects.create(
            user = bot2,
            id_list = [],
        )
        self.assertEqual(
            is_follower(su.user_id, bot1.profile.json["screen_name"]),
            False
        )
        self.assertEqual(
            is_follower(su.user_id, bot2.profile.json["screen_name"]),
            False
        )
        """
        su is following account1 of community 1
        su is NOT following account2 of community 2
        (account1 is among follower_common_account of account2)
        (account2 is among follower_common_account of account1)
        is_follower(su.user_id, username1) should be True
        is_follower(su.user_id, username2) should be True
        """
        community1.follower_common_account.clear()
        community2.follower_common_account.clear()
        community1.follower_common_account.add(account2)
        community2.follower_common_account.add(account1)
        Follower.objects.all().delete()
        Follower.objects.create(
            user = bot1,
            id_list = [su.user_id],
        )
        Follower.objects.create(
            user = bot2,
            id_list = [],
        )
        self.assertEqual(
            is_follower(su.user_id, bot1.profile.json["screen_name"]),
            True
        )
        self.assertEqual(
            is_follower(su.user_id, bot2.profile.json["screen_name"]),
            True
        )
        """
        su is NOT following account1 of community 1
        su is following account2 of community 2
        (account1 is among follower_common_account of account2)
        account2 is among follower_common_account of account1
        is_follower(su.user_id, username1) should be True
        is_follower(su.user_id, username2) should be True

        """
        community1.follower_common_account.clear()
        community2.follower_common_account.clear()
        community1.follower_common_account.add(account2)
        community2.follower_common_account.add(account1)
        Follower.objects.all().delete()
        Follower.objects.create(
            user = bot1,
            id_list = [],
        )
        Follower.objects.create(
            user = bot2,
            id_list = [su.user_id],
        )
        self.assertEqual(
            is_follower(su.user_id, bot1.profile.json["screen_name"]),
            True
        )
        self.assertEqual(
            is_follower(su.user_id, bot2.profile.json["screen_name"]),
            True
        )
        """
        su is following account1 of community 1
        su is following account2 of community 2
        account1 is among follower_common_account of account2
        account2 is among follower_common_account of account1
        is_follower(su.user_id, username1) should be True
        is_follower(su.user_id, username2) should be True
        """
        community1.follower_common_account.clear()
        community2.follower_common_account.clear()
        Follower.objects.all().delete()
        Follower.objects.create(
            user = bot1,
            id_list = [su.user_id],
        )
        Follower.objects.create(
            user = bot2,
            id_list = [su.user_id],
        )
        self.assertEqual(
            is_follower(su.user_id, bot1.profile.json["screen_name"]),
            True
        )
        self.assertEqual(
            is_follower(su.user_id, bot2.profile.json["screen_name"]),
            True
        )
        