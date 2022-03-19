import logging
import time
from django.core.management.base import BaseCommand, CommandError
from conversation.tasks import handle_all_text_search_vector
from conversation.models import Tweetdj

logger=logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fill status_text SearchVectorField column'

    def add_arguments(self, parser):
        parser.add_argument(
            'n',
            type=int,
            help="number of Tweetdj objects to process",
        )

    def handle(self, *args, **options):
        n = options["n"]
        logger.debug(n)
        total = Tweetdj.objects.count()
        done0 = Tweetdj.objects.filter(status_text__isnull=False).count()
        percent = "{:.2f}".format(done0 / total * 100)
        self.stdout.write(
            self.style.SUCCESS(
                f'{done0} total SearchVector fields.\n'
                f'{percent}% of all {total} statuses.'
            )
        )
        start_time = time.time()
        handle_all_text_search_vector(n)
        stop_time = time.time()
        elapsed = stop_time - start_time
        done1 = Tweetdj.objects.filter(status_text__isnull=False).all().count()
        processed = done1-done0
        processed_per_second = "{:.2f}".format(processed / elapsed)
        percent = "{:.2f}".format(done1 / total * 100)
        self.stdout.write(
            self.style.SUCCESS(
                f'{processed} statuses processed successfully.\n'
                f'{done1} total SearchVector fields.\n'
                f'{percent}% of all {total} statuses.\n'
                f'--- {elapsed} seconds ---\n'
                f'{processed_per_second} Tweetdj per second'
            )
        )