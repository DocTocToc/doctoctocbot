from django.core.management.base import BaseCommand, CommandError
import time
from conversation.utils import retweeted_by
from conversation.models import Tweetdj

current_time = int(time.time())

class Command(BaseCommand):
    help = 'Update retweeted_by'
        
    def handle(self, *args, **options):
        for status in Tweetdj.objects.all():
            if status.retweetedstatus and status.json and status.socialuser:
                try:
                    rt_statusid = status.json["retweeted_status"]["id"]
                except KeyError:
                    continue
                try:
                    rt_userid = status.json["retweeted_status"]["user"]["id"]
                except KeyError:
                    continue
                retweeted_by(
                    rt_statusid = rt_statusid,
                    rt_userid = rt_userid,
                    by_socialuserid = status.socialuser.id,
                )
        self.stdout.write(self.style.SUCCESS('Done.'))