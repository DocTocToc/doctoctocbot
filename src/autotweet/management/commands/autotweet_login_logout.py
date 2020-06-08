from django.core.management.base import BaseCommand, CommandError

from autotweet.login import AutoLogin
from autotweet.utils import rnd_str_gen, tweet, sleep

class Command(BaseCommand):
    help = 'Test Twitter Selenium autotweet: login, tweet and logout'

    def add_arguments(self, parser):
        parser.add_argument('username')


    def handle(self, *args, **options):
        username = options['username']
        self.stdout.write(
            self.style.SUCCESS(
                'Username is: "%s"' % username
            )
        )  
        autologin = AutoLogin(username)
        sleep()
        autologin.login_mobile_twitter()
        sleep()
        tweet(rnd_str_gen(size=20))
        sleep()
        autologin.logout()
        self.stdout.write(
            self.style.SUCCESS(
                'User "%s" successfully logged in & out of Twitter' % username
            )
        )