import csv
import logging
from django.core.management.base import BaseCommand, CommandError
from hcp.models import Taxonomy
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Upload the content of the specified CVS file into Taxonomy table'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        path = options['path']
        if not path:
            return
        try:
            with open(path) as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        _, created = Taxonomy.objects.get_or_create(
                            code=row[0],
                            grouping_en=row[1],
                            classification_en=row[2],
                            specialization_en=row[3],
                            definition_en=row[4],
                        )
                    except:
                        logger.error(f"Error with row: {row}")
                    if not created:
                        logger.info(f"Row {row} already exists")
                        
        except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
            self.stdout.write(self.style.SUCCESS('Could not open file at "%s"' % path))
            return

        self.stdout.write(self.style.SUCCESS('Successfully uploaded data from "%s"' % path))