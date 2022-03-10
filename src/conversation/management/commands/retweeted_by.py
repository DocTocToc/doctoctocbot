from django.core.management.base import BaseCommand, CommandError
import time
from conversation.models import Tweetdj
from moderation.social import get_socialuser_from_screen_name
from conversation.retweet import RetweetedBy
current_time = int(time.time())

class Command(BaseCommand):
    help = 'Update retweeted_by'

    def add_arguments(self, parser):
        parser.add_argument('screen_name', type=str)
        parser.add_argument('--batch', '-b', type=int)
        
    def handle(self, *args, **options):
        screen_name = options["screen_name"]
        su = get_socialuser_from_screen_name(screen_name)
        if not su:
            self.stdout.write(
                self.style.ERROR(
                    'No SocialUser found for {}'.format(screen_name)
                )
            )
            return
        batch = options['batch'] or 1000
        rtby = RetweetedBy(su, batch)
        count0=rtby.count()
        self.stdout.write(
            self.style.WARNING(
                    f'Tweetdj objects retweeted by {su}: {count0}'
            )
        )
        rtby.process()
        count1=rtby.count()
        added = count1-count0
        self.stdout.write(
            self.style.SUCCESS(f'Done. {added} rt_by added.')
        )