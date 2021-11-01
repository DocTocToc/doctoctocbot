import logging
from bot.follow import Follow
from moderation.social import get_socialuser_from_screen_name
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
    help = 'Create friendships based on categories and prospects'
    
    def add_arguments(self, parser):
        parser.add_argument(
            "screen_name",
            type=str,
            help="Twitter account's screen_name"
        )
        parser.add_argument(
            "-c",
            "--count",
            type=int,
            help="count represents the number of friendships to create"
        )
        parser.add_argument(
            "-d",
            "--days",
            type=int,
            help="create friendship this many days after last creation"
        )
        parser.add_argument(
            "-s",
            "--sample",
            type=int,
            help="size of a random sample of socialusers to process"
        )
        parser.add_argument(
            '--force-follow',
            dest='force_follow',
            action='store_true'
        )
        parser.set_defaults(force_follow=False)

    def handle(self, *args, **options):
        screen_name: str =  options['screen_name']
        count: int = options['count']
        days: int = options['days']
        force_follow = options['force_follow']
        sample = options['sample']
        logger.debug(f'{force_follow=}')
        socialuser = get_socialuser_from_screen_name(screen_name)
        if not socialuser:
            self.stdout.write(
                self.style.ERROR(
                    'No SocialUser found for screen_name "%s"' % screen_name
                )
            )
            return
        if count is None or count > 100 or count < 0:
            self.stdout.write(
                self.style.ERROR(
                    'count is %s, it should be a positive integer <= 100' % count
                )
            )
            return
        follow = Follow(
            socialuser=socialuser,
            count=count,
            delta=days,
            force_follow=force_follow,
            sample=sample,
        )
        followed_dict = follow.process()
        self.stdout.write(
            self.style.SUCCESS(
                followed_dict
            )
        )