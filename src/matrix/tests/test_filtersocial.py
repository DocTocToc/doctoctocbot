import string
import logging
from matrix.cas.callbacks import filtersocial
from django.test import TestCase, override_settings
from matrix.tests import factories
from community.models import Community
from bot.models import Account
from moderation.models import Follower, SocialUser, SocialMedia, Profile
from bot.doctoctocbot import is_follower

logger = logging.getLogger(__name__)


class IsFollowerTestCase(TestCase):
    def setUp(self):
        pass

    def test_filtersocial1(self):
        factories.SocialMediaFactory()
        categories = factories.CategoryFactory.create_batch(3)
        socialusers = factories.SocialUserFactory.create_batch(4)
        socialusers[1].category.add(categories[0])
        socialusers[2].category.add(categories[1])
        socialusers[3].category.add(categories[2])
        logger.debug(socialusers[0])
        f = factories.FollowerFactory(
            user=socialusers[0],
            id_list=[
                socialusers[1].user_id,
                socialusers[2].user_id,
                socialusers[3].user_id,
            ]
        )
        logger.debug(f"{f=} {f.user=} {f.id_list=}")
        fs = factories.FilterSocialFactory(
            follower_lower=2
        )
        fs.follower_category.add(
            categories[0],
            categories[1]
        )
        user = factories.UserFactory(socialuser=socialusers[0])
        self.assertEqual(
            filtersocial(user),
            True
        )

    def test_filtersocial2(self):
        factories.SocialMediaFactory()
        categories = factories.CategoryFactory.create_batch(3)
        socialusers = factories.SocialUserFactory.create_batch(4)
        socialusers[1].category.add(categories[0])
        socialusers[2].category.add(categories[2])
        socialusers[3].category.add(categories[2])
        logger.debug(socialusers[0])
        f = factories.FollowerFactory(
            user=socialusers[0],
            id_list=[
                socialusers[1].user_id,
                socialusers[2].user_id,
                socialusers[3].user_id,
            ]
        )
        logger.debug(f"{f=} {f.user=} {f.id_list=}")
        fs = factories.FilterSocialFactory(
            follower_lower=2
        )
        fs.follower_category.add(
            categories[0],
            categories[1]
        )
        user = factories.UserFactory(socialuser=socialusers[0])
        self.assertEqual(
            filtersocial(user),
            False
        )