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
            "--sample_size",
            type=int,
            help="size of a random sample of socialusers to process"
        )
        parser.add_argument(
            '--force',
            dest='force',
            action='store_true'
        )
        parser.set_defaults(force=False)
        parser.add_argument(
            "-p",
            "--sleep",
            type=int,
            help=(
                "The bot will pause this number of seconds between two "
                "friendship creation API requests"
            )
        )

    def handle(self, *args, **options):
        screen_name: str =  options['screen_name']
        count: int = options['count']
        days: int = options['days']
        force = options['force']
        sample_size = options['sample_size']
        sleep = options['sleep']
        socialuser = get_socialuser_from_screen_name(screen_name)
        if not socialuser:
            self.stdout.write(
                self.style.ERROR(
                    'No SocialUser found for screen_name "%s"' % screen_name
                )
            )
            return
        if count is None or count > 20 or count < 0:
            self.stdout.write(
                self.style.ERROR(
                    'count is %s, it should be a positive integer <= 20' % count
                )
            )
            return
        follow = Follow(
            socialuser=socialuser,
            count=count,
            delta=days,
            force=force,
            sample_size=sample_size,
            sleep=sleep,
        )
        followed_dict = follow.process()
        self.stdout.write(
            self.style.SUCCESS(
                followed_dict
            )
        )