from django.core.management.base import BaseCommand, CommandError
import tweepy                                                                   
from bot.tweepy_api import getAuth                                                     
from bot.lib.statusdb import Addstatus
from tweepy import TweepError

class Command(BaseCommand):
    help = 'Add status to database'

    def add_arguments(self, parser):
        parser.add_argument('statusid', nargs='+', type=int)

    def handle(self, *args, **options):
        count=0
        status_ids = options['statusid']
        API = tweepy.API(getAuth())
        if len(status_ids) == 1:
            try:
                status = API.get_status(status_ids[0], tweet_mode='extended')
            except TweepError as e:
                self.stdout.write(
                    self.style.ERROR(
                    'Error while retrieving status %s, %s' % status_ids[0], e
                )
            )
                return
            db = Addstatus(status._json)
            _, created = db.addtweetdj()
            if created:
                count+=1
                self.stdout.write(
                    self.style.SUCCESS(
                        'Successfully added status %s to database'
                        % status_ids[0]
                    )
                )
        else:
            chunk_size = 100
            for i in range(0, len(status_ids), chunk_size):
                ids = status_ids[i:i+chunk_size]
                try:
                    statuses = API.statuses_lookup(ids, tweet_mode='extended')
                except TweepError as e:
                    self.stdout.write(
                        self.style.ERROR(
                        'Error while retrieving statuses: %s' %  e
                    )
                )
                for status in statuses:
                    db = Addstatus(status._json)
                    _, created = db.addtweetdj()
                    if created:
                        count+=1
                        self.stdout.write(
                            self.style.SUCCESS(
                                'Successfully added status %s to database'
                                % status_ids[0]
                            )
                        )
        self.stdout.write(
                        self.style.SUCCESS(
                            'Successfully added %s status  to database'
                            % count
                        )
                    )