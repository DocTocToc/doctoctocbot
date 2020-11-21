from django.core.management.base import BaseCommand, CommandError

from conversation.models import create_leaf, Tweetdj

class Command(BaseCommand):
    help = 'Add known leaves'
        
    def handle(self, *args, **options):
        count = 0  
        for tweetdj in Tweetdj.objects.filter(json__in_reply_to_status_id__isnull=False):
            leaf = create_leaf(
                tweetdj.statusid,
                tweetdj.json["in_reply_to_status_id"]
            )
            if leaf:
                count += 1
        self.stdout.write(self.style.SUCCESS(f'{count} leaves added.'))