from django.core.management.base import  BaseCommand, CommandError
from conversation.models import Tweetdj
from status.models import Status

class Command(BaseCommand):
    help = 'Transfer tweets from prodstatus DB (Status model) to Doctocnet DB (Tweetdj model)'
    
    def handle(self, *args, **options):
        for status_mi in Status.objects.using('status').all():
            Tweetdj.objects.create(
                statusid=status_mi.id,
                userid=status_mi.userid,
                json=status_mi.json,
                created_at=status_mi.datetime)
        self.stdout.write(self.style.SUCCESS('Done transferring data.'))