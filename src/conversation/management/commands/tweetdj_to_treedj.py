from django.core.management.base import BaseCommand, CommandError
from conversation.tree.utils import add_tweetdj_to_treedj
from conversation.models import Treedj

class Command(BaseCommand):
    help = 'Add known leaves but faster'
     
    def handle(self, *args, **options):
        count0 = Treedj.objects.count()  
        add_tweetdj_to_treedj()
        count1 = Treedj.objects.count()
        count = count1 - count0
        if count==0:
            message="No new leaf added."
        elif count==1:
            message="1 leaf added."
        else:
            message=f'{count1-count0} leaves added.'
        self.stdout.write(self.style.SUCCESS(message))