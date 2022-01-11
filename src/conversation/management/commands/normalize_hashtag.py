from django.core.management.base import BaseCommand, CommandError
from conversation.utils import bulk_hashtag
from conversation.models import Hashtag
from django.db.models import Q

class Command(BaseCommand):
    help = 'Fill hashtag m2m field from json data'

    def add_arguments(self, parser):
        parser.add_argument('hashtag', nargs='+', type=str)

    def handle(self, *args, **options):
        hashtags = options['hashtag']
        hashtag_filter = Q()
        for hashtag in hashtags:
            hashtag_filter |= Q(hashtag__iexact=hashtag)
        h_qs = Hashtag.objects.filter(hashtag_filter)
        if not h_qs:
            self.stdout.write(
                self.style.ERROR(
                    'Error: no corresponding Hashtag objects found in db.'
                )
            )
            return
        for hashtag in h_qs:
            bulk_hashtag(hashtag)
        self.stdout.write(
            self.style.SUCCESS(
                "Done"
            )
        )