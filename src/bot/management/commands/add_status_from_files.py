from django.core.management.base import BaseCommand, CommandError
from os import listdir
from os.path import isfile, join
import json
from bot.log.log import setup_logging
#import logging
from bot.lib.statusdb import Addstatus

#logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Add status to database from files'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        path = options['path']
        files = [f for f in listdir(path) if isfile(join(path, f))]
        for file in files:
            with open(join(path, file), 'r') as f:
                jsn = json.loads(f.read())
                #logger.debug(json.dumps(jsn))
                db = Addstatus(jsn)
                db.addtweetdj()
            self.stdout.write(self.style.SUCCESS('Successfully added status "%s" to database' % jsn["id"]))
        