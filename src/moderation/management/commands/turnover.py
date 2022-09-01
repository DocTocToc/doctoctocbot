""" Display followers' departures and arrivals """

import logging
import datetime
from typing import List

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import DatabaseError
from django.utils import timezone

from moderation.models import (
    Follower,
    SocialUser,
    Category,
    UserCategoryRelationship,
)
from community.models import Community
from bot.tweepy_api import get_api
from moderation.social import update_social_ids
from tweepy import TweepError

logger = logging.getLogger(__name__)


def display_socialusers(qs, api, check_user=False):
    _str = ""
    for su in qs:
        screen_name = su.screen_name_tag()
        _str+=f'@{screen_name}'
        if check_user:
            try:
                api.get_user(screen_name)
            except TweepError as e:
                _str+= f': {e.args[0][0]["message"]}'
        _str+='\n'
    return _str

class Command(BaseCommand):
    help = "Display followers' departures and arrivals"

    def add_arguments(self, parser):
        parser.add_argument('community', type=str)
        parser.add_argument(
            "-d",
            "--days",
            type=int,
            help="Since this number of days"
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help="Update followers' list",
        )

    def handle(self, *args, **options):
        community_name: str = options['community']
        days: int =  options['days'] or 1
        delta = datetime.timedelta(days=days)
        cutoff_dt: datetime = timezone.now() - delta 
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
        bot_su = community.account.socialuser
        if options["update"]:
            update_social_ids(
                bot_su,
                cached=False,
                bot_screen_name=bot_su.screen_name_tag(),
                relationship='followers',
            )
        try:
            followers_now = Follower.objects.filter(user=bot_su).latest()
            logger.debug(
                f'{followers_now=} '
                f'{followers_now.id_list=}'
                f'{len(followers_now.id_list)=}'
            )
        except Follower.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f'No Follower entry for {bot_su}.'
                    'Use --update flag to create one.'
                )
            )
            return
        try:
            followers_then = Follower.objects.filter(
                user=bot_su,
                created__lte=cutoff_dt,
            ).latest()
            logger.debug(
                f'{followers_then=} '
                f'{followers_then.id_list=} '
                f'{len(followers_then.id_list)=}'
            )
        except Follower.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f'No Follower entry for {bot_su} existed more than {days} '
                    'ago.'
                )
            )
            return
        arrivals = set(followers_now.id_list) - set(followers_then.id_list)
        logger.debug(arrivals)
        departures = set(followers_then.id_list) - set(followers_now.id_list)
        logger.debug(departures)
        arrivals_qs = SocialUser.objects.filter(user_id__in=arrivals)
        logger.debug(arrivals_qs)
        departures_qs = SocialUser.objects.filter(user_id__in=departures)
        logger.debug(departures_qs)
        api=get_api(username=community.account.username)
        self.stdout.write(
            self.style.SUCCESS(
                f'New followers of {bot_su.screen_name_tag()} '
                f'since {days} day(s) ago:\n'
                f'{display_socialusers(arrivals_qs, api, check_user=False) or None}\n'
                f'Users who unfollowed {bot_su.screen_name_tag()} '
                f'since {days} day(s) ago:\n'
                f'{display_socialusers(departures_qs, api, check_user=True) or None}\n'
            )
        )