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
            "-s",
            "--screen_name",
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

    def handle(self, *args, **options):
        users: List =  options['users']
        screen_name: str =  options['screen_name']
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
        self.moderator=get_socialuser_from_screen_name(screen_name)
        logger.debug(self.moderator)
        categorize: bool = self.category and self.moderator and self.community
        if not users:
            self.stdout.write(
                self.style.ERROR(
                    'You must provide one or more username(s) or userid(s).'
                )
            )
            return
        for user in users:
            user_id = None
            screen_name = None
            try:
                user_id=int(user)
                try:
                    su = SocialUser.objects.get(user_id=user_id)
                    self.stdout.write(
                        self.style.ERROR(
                            f'SocialUser object with user id {user_id} '
                            'already exists.'
                        )
                    )
                    if categorize:
                        self.create_user_category_relationship(su)
                    continue
                except SocialUser.DoesNotExist:
                    pass
            except ValueError:
                screen_name = user
            if screen_name:
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
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Done creating SocialUser object {su}.'
                    )
                )
            elif su:
                self.stdout.write(
                    self.style.ERROR(
                        f'SocialUser object {su} already exists.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error, no new user was created.'
                    )
                )
            if su:
                self.create_user_category_relationship(su)