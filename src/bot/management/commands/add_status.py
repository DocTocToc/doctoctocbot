from django.core.management.base import BaseCommand, CommandError
import tweepy                                                                   
from bot.tweepy_api import getAuth                                                     
from bot.lib.statusdb import Addstatus

class Command(BaseCommand):
    help = 'Add status to database'

    def add_arguments(self, parser):
        parser.add_argument('statusid', nargs='+', type=int)

    def handle(self, *args, **options):
        for statusid in options['statusid']:
            API = tweepy.API(getAuth())

            status = API.get_status(statusid, tweet_mode='extended')
            db = Addstatus(status._json)
            db.addtweetdj()
            self.stdout.write(self.style.SUCCESS('Successfully added status "%s" to database' % statusid))