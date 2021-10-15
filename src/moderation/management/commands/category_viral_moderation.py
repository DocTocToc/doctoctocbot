"""
Try to turn all users from a given category into moderators according to
viral moderation settings.
"""

from typing import List
from django.core.management.base import BaseCommand, CommandError
from moderation.dm import viral_moderation
from moderation.models import (
    SocialUser,
    SocialMedia,
    Category,
    UserCategoryRelationship,
    Moderator,
)
from community.models import Community
from moderation.social import update_social_ids
from bot.tweepy_api import get_api
from tweepy.error import TweepError
from tweepy.models import User
from django.db.utils import DatabaseError

class Command(BaseCommand):
    help = ('turn all users from a given category into moderators according to '
            'viral moderation settings')
    
    def add_arguments(self, parser):
        parser.add_argument(
            '-cat',
            '--category',
            nargs='?',
            type=str,
            help='Indicates the category to process'
        )

    def handle(self, *args, **kwargs):
        category_name = kwargs['category']
        try:
            category_mi= Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR("This community does not exist."))
            return
        try:
            socialmedia_mi = SocialMedia.objects.get(name='twitter')
        except SocialMedia.DoesNotExist:
            return
        socialuser_qs = SocialUser.objects.filter(
            category=category_mi,
            social_media=socialmedia_mi
        )
        counter = 0
        for socialuser in socialuser_qs:
            ok = viral_moderation(socialuser.id, cached=True)
            if ok:
                counter += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Success. {counter} user(s) turned into moderator(s)"
            )
        )