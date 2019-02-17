import pytz

from django.core.management.base import BaseCommand, CommandError
from django.core.paginator import Paginator
from django.conf import settings

from conversation.models import Tweetdj
from status.models import Status


class Command(BaseCommand):
    help = 'Transfer tweets from prodstatus DB (Status model) to Doctocnet DB (Tweetdj model)'
    
    def handle(self, *args, **options):
        paginator = Paginator(Status.objects.using('status').all(), settings.PAGINATION)
        for page_idx in paginator.page_range:
            for status_mi in paginator.page(page_idx).object_list:
                Tweetdj.objects.create(
                    statusid=status_mi.id,
                    userid=status_mi.userid,
                    json=status_mi.json,
                    created_at=status_mi.datetime.replace(tzinfo=pytz.UTC))
        self.stdout.write(self.style.SUCCESS('Done transferring data.'))