from typing import List

from django.core.management.base import BaseCommand, CommandError

from autotweet.login import AutoLogin
from autotweet.utils import rnd_str_gen, tweet, sleep
from moderation.social import get_socialuser_from_screen_name

class Command(BaseCommand):
    help = 'Twitter Selenium autotweet: login, authorize and logout'

    def add_arguments(self, parser):
        parser.add_argument(
            '--account',
            help='screen_name of the account'
        )
        parser.add_argument(
            '--follower',
            nargs='+',
            help='screen_name of the followers to accept'
        )

    def handle(self, *args, **options):
        account_username = options['account']
        follower_screen_name_lst: List = options['follower']
        autologin = AutoLogin(account_username)
        sleep()
        autologin.login_mobile_twitter()
        sleep()
        tweet(rnd_str_gen(size=20))
        uids = []
        for sn in follower_screen_name_lst:
            su = get_socialuser_from_screen_name(sn)
            if su:
                uids.append(su.user_id)
        # accept follow requests here
        res = None
        self.stdout.write(
            self.style.SUCCESS(
                'Response: "%s"' % res
            )
        )
        sleep()
        autologin.logout()
        self.stdout.write(
            self.style.SUCCESS(
                'User "%s" successfully logged in & out of Twitter' % account_username
            )
        )