from django.core.management.base import BaseCommand, CommandError
from conversation.tree.utils import add_tweetdj_to_treedj
from conversation.models import Treedj

def count():
    return Treedj.objects.count()

def msg(count):
    if count==0:
        return "No new leaf added."
    elif count==1:
        return "1 leaf added."
    else:
        return f'{count} leaves added.'

class Command(BaseCommand):
    help = 'Add known leaves but faster'

    def handle(self, *args, **options):
        total_counter0 = count()
        while True:
            counter0 = count()
            add_tweetdj_to_treedj()
            counter1 = count()
            counter = counter1 - counter0
            self.stdout.write(self.style.WARNING(f"{msg(counter)}"))
            if not counter:
                break
        total_counter1 = count()
        total_counter = total_counter1 - total_counter0
        self.stdout.write(self.style.SUCCESS(f"Total: {msg(total_counter)}"))