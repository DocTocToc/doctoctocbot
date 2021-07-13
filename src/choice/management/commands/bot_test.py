from choice.matrix import main
from django.core.management.base import BaseCommand, CommandError
import logging
import asyncio
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test Matrix bot'
    
    def add_arguments(self, parser):
        pass
        #parser.add_argument('text', type=str)
    
    def handle(self, *args, **options):
        #text = options['text']
        #logger.debug(f"{text=}")
        #if not text:
        #    self.stdout.write(self.style.ERROR('Add a text.'))
        try:
            asyncio.run(
                main()
            )
        except KeyboardInterrupt:
            pass
        self.stdout.write(self.style.SUCCESS('Done testing Matrix bot.'))