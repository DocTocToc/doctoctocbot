from django.core.management.base import BaseCommand, CommandError

from community.models import Community
from autotweet.authentication import get_auth_driver_chrome
from autotweet.utils import rnd_str_gen, tweet_desktop, sleep

class Command(BaseCommand):
    help = 'Test Twitter Selenium autotweet with Chrome standalone driver: login, tweet and logout'

    def add_arguments(self, parser):
        parser.add_argument('community')


    def handle(self, *args, **options):
        community_name = options['community']
        try:
            community = Community.objects.get(name=community_name)
        except Community.DoesNotExist:
            return
        driver = get_auth_driver_chrome(community)
        sleep()
        tweet_desktop(rnd_str_gen(size=20), driver=driver)
        sleep()
        self.stdout.write(
            self.style.SUCCESS(
                'User "%s" successfully logged in & out of Twitter' % community.account.username
            )
        )