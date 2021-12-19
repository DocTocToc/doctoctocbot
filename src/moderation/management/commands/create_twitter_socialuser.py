""" Create a Twitter SocialUser object from userid or screen_name """

import logging
from django.core.management.base import BaseCommand, CommandError
from moderation.profile import create_twitter_social_user_and_profile
from community.models import Community
from moderation.models import SocialUser, Category, UserCategoryRelationship
from bot.tweepy_api import get_api
from tweepy.error import TweepError
from typing import List
from moderation.social import get_socialuser_from_screen_name

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create SocialUser object from userids or screen names'

    def add_arguments(self, parser):
        parser.add_argument('users', nargs='+', type=str)
        parser.add_argument(
            "-c",
            "--category",
            type=str,
            help="category name"
        )
        parser.add_argument(
            "-m",
            "--moderator",
            type=str,
            help="moderator screen_name"
        )
        parser.add_argument(
            "-k",
            "--community",
            type=str,
            help="community name"
        )

    def create_user_category_relationship(self, su):
        try:
            UserCategoryRelationship.objects.create(
                social_user=su,
                category=self.category,
                moderator=self.moderator,
                community=self.community,
            )
        except:
            return

    def process_user_id(self, user_id):
        try:
            su = SocialUser.objects.get(user_id=user_id)
            self.stdout.write(
                self.style.WARNING(
                    f'SocialUser object with user id {user_id} already exists.'
                )
            )
            if self.categorize:
                self.create_user_category_relationship(su)
        except SocialUser.DoesNotExist:
            return

    def process_screen_name(self, screen_name: str):
        api = get_api()
        if not api:
            self.stdout.write(
                self.style.ERROR(
                    f'Could not get functional API.'
                )
            )
            return
        try:
            tweepy_user = get_api().get_user(screen_name=screen_name)
        except TweepError as e:
            raise CommandError('Tweepy error "%s' % e)
        except AttributeError as e:
            logger.error(f"AttributeError: {e}")
            return
        user_id=tweepy_user.id
        self.stdout.write(f"user id: {user_id}")
        su, created = create_twitter_social_user_and_profile(user_id)
        if created and su:
            su.refresh_from_db()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Done creating SocialUser object {su}.'
                )
            )
        elif su:
            self.stdout.write(
                self.style.SUCCESS(
                    f'SocialUser object {su} already exists. '
                    'Its profile was updated.'
                )
            )
            current_screen_name = su.screen_name_tag()
            if not (current_screen_name == screen_name):
                self.stdout.write(
                    self.style.WARNING(
                        f'screen_name of SocialUser {su} has changed!\n'
                        f'old: "{screen_name}" -> new: "{current_screen_name}"'
                    )
                )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'Error, no SocialUser was created.'
                )
            )
            return
        if su and self.categorize:
            self.create_user_category_relationship(su)

    def handle(self, *args, **options):
        users: List =  options['users']
        mod_screen_name: str =  options['moderator']
        category: str =  options['category']
        community: str =  options['community']
        try:
            self.category=Category.objects.get(name=category)
            logger.debug(self.category)
        except Category.DoesNotExist:
            self.category=None
        try:
            self.community=Community.objects.get(name=community)
            logger.debug(self.community)
        except Community.DoesNotExist:
            self.community=None
        if mod_screen_name:
            self.moderator = get_socialuser_from_screen_name(mod_screen_name)
            if not self.moderator:
                self.stdout.write(
                    self.style.ERROR(
                        f'SocialUser {mod_screen_name=} does not exist.'
                    )
                )
                return
        self.categorize: bool = (
            self.category
            and self.moderator
            and self.community
        )
        if not users:
            self.stdout.write(
                self.style.ERROR(
                    'You must provide one or more username(s) or userid(s).'
                )
            )
            return
        for user in users:
            try:
                user_id=int(user)
                self.process_user_id(user_id)
            except ValueError:
                self.process_screen_name(user)