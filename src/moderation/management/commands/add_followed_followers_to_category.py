"""
Add all users who are both friends and followers from a given community to a
given category.
"""

from typing import List
from django.core.management.base import BaseCommand, CommandError

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
    help = 'Create SocialUser object from userid or screen name'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '-com',
            '--community',
            nargs='?',
            type=str,
            help='Indicates the community these changes should be applied to'
        )
        parser.add_argument(
            '-cat',
            '--category',
            nargs='?',
            type=str,
            help='Indicates the category these users should be added in'
        )

    def handle(self, *args, **kwargs):
        community_name = kwargs['community']
        category_name = kwargs['category']
        try:
            community_mi= Community.objects.get(name=community_name)
        except Community.DoesNotExist:
            self.stdout.write(self.style.ERROR("This community does not exist."))
            return       
        try:
            category_mi= Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR("This community does not exist."))
            return
        try:
            bot_username = community_mi.account.username
            bot_userid = community_mi.account.userid
        except:
            self.stdout.write(
                self.style.ERROR("We could not retrieve the account of this community")
            )
            return
        # get friends
        friends: List[int] = update_social_ids(
            bot_username,
            cached=False,
            bot_screen_name=bot_username,
            relationship='friends',
        )
        # get followers
        followers: List[int] = update_social_ids(
            bot_username,
            cached=False,
            bot_screen_name=bot_username,
            relationship='followers',
        )
        inter_ids: List[int] = list(set(friends) & set(followers))
        n = 100
        split: List[List[int]] = [inter_ids[i:i+n] for i in range(0, len(inter_ids), n)]
        api = get_api(username=bot_username)
        try:
            twitter = SocialMedia.objects.get(name='twitter')
        except SocialMedia.DoesNotExist:
            return
        try:
            bot_su = SocialUser.objects.get(user_id=bot_userid)
        except SocialUser.DoesNotExist:
            return
        for ids in split:
            users: List[User] = api.lookup_users(ids)
            for user in users:
                try:
                    su, _ = SocialUser.objects.get_or_create(
                        user_id = user.id,
                        social_media = twitter
                    )
                except DatabaseError:
                    continue
                try:
                    _ucr, _ = UserCategoryRelationship.objects.get_or_create(
                        social_user = su,
                        category = category_mi,
                        moderator = bot_su,
                        community = community_mi
                    )
                except DatabaseError:
                    continue
                # add SocialUser to Moderator table
                if not Moderator.objects.filter(
                    socialuser=su,
                    community=community_mi
                ).exists():
                    try:
                        Moderator.objects.create(
                            socialuser=su,
                            community=community_mi,
                            active=True,
                        )
                    except DatabaseError:
                        continue
        self.stdout.write(
            self.style.SUCCESS(
                f"Success. {len(inter_ids)} users processed"
            )
        )