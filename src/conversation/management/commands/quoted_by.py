from django.core.management.base import BaseCommand, CommandError
import time
from conversation.utils import quoted_by
from conversation.models import Tweetdj

current_time = int(time.time())

class Command(BaseCommand):
    help = 'Update quoted_by'
        
    def handle(self, *args, **options):
        for status in Tweetdj.objects.all():
            if status.quotedstatus and status.json and status.socialuser:
                try:
                    quoted_statusid = status.json["quoted_status"]["id"]
                except KeyError:
                    continue
                try:
                    quoted_userid = status.json["quoted_status"]["user"]["id"]
                except KeyError:
                    continue
                quoted_by(
                    quoted_statusid = quoted_statusid,
                    quoted_userid = quoted_userid,
                    by_socialuserid = status.socialuser.id,
                )
        self.stdout.write(self.style.SUCCESS('Done.'))