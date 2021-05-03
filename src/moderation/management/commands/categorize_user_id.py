""" Create a Twitter SocialUser object from userid or screen_name """

import logging
from django.core.management.base import BaseCommand, CommandError
from moderation.profile import create_twitter_social_user_and_profile
from moderation.models import SocialUser, Category, UserCategoryRelationship
from community.models import Community
from bot.tweepy_api import get_api
from tweepy.error import TweepError
from typing import List
from django.db.utils import DatabaseError

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create SocialUser object from userids or screen names'
    
    def add_arguments(self, parser):
        parser.add_argument('users', nargs='+', type=str)
        parser.add_argument(
            "-c",
            "--category",
            type=str,
            help="users will be added to this category"
        )
        parser.add_argument(
            "-m",
            "--moderator",
            type=int,
            help="SocialUser id of the moderator of the new UserCategoryRelatioship"
        )
        parser.add_argument(
            "-k",
            "--community",
            type=str,
            help="name of the community of the new UserCategoryRelatioship"
        )
    def handle(self, *args, **options):
        users: List =  options['users']
        category: str = options['category']
        moderator_id: int = int(options['moderator'])
        community_name: str = options['community']
        try:
            category = Category.objects.get(name=category)
        except Category.DoesNotExist as e:
            logger.error(e)
            self.stdout.write(
                self.style.ERROR(
                    f'Category {category} does not exist.'
                )
            )
            return
        try:
            community = Community.objects.get(name=community_name)
        except Community.DoesNotExist as e:
            logger.error(e)
            self.stdout.write(
                self.style.ERROR(
                    f'Community {community_name} does not exist.'
                )
            )
            return
        try:
            moderator = SocialUser.objects.get(id=moderator_id)
        except SocialUser.DoesNotExist as e:
            logger.error(e)
            self.stdout.write(
                self.style.ERROR(
                    f'SocialUser with id: {moderator_id} does not exist.'
                )
            )
            return
        for user in users:
            try:
                user_id=int(user)
            except ValueError:
                continue
            try:
                su = SocialUser.objects.get(user_id=user_id)
            except SocialUser.DoesNotExist as e:
                logger.error(e)
                self.stdout.write(
                    self.style.ERROR(
                        f'SocialUser object with user id {user_id} '
                        'does not exist.'
                    )
                )
                continue
            try:
                ucr = UserCategoryRelationship.objects.create(
                    category = category,
                    social_user = su,
                    moderator=moderator,
                    community=community,
                )
                self.stdout.write(
                    self.style.ERROR(
                        f'ucr: {ucr} created.'
                    )
                )
            except DatabaseError as e:
                logger.error(e)
                continue