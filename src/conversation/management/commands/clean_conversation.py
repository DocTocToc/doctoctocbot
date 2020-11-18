from django.core.management.base import BaseCommand, CommandError
import time

from conversation.utils import feed_tree
from conversation.models import create_tree
from conversation.models import Tweetdj, Treedj
from bot.lib.snowflake import snowflake2utc

current_time = int(time.time())

class Command(BaseCommand):
    help = 'Delete fake status from Tweetdj Treedj'
        
    def handle(self, *args, **options):
        deleted_id = []
        for status in Tweetdj.objects.all():
            if snowflake2utc(status.statusid) > current_time:
                status.delete()
                deleted_id.append(status.statusid)
        for statusid in deleted_id:
            try:
                t = Treedj.objects.get(statusid=statusid)
                t.delete()
            except Treedj.DoesNotExist:
                continue
        self.stdout.write(self.style.SUCCESS('DB cleaned.'))