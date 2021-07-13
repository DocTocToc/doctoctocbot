from choice.matrix import main
from django.core.management.base import BaseCommand, CommandError
import logging
import asyncio
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test Matrix bot'
    
    def add_arguments(self, parser):
        parser.add_argument('--user_id', type=str, required=True)
        parser.add_argument('--room_alias', type=str)
        parser.add_argument('--room_name', type=str)
        parser.add_argument('--room_subject', type=str)
        parser.add_argument('--greeting', type=str)
    
    def handle(self, *args, **options):
        user_id = options['user_id']
        logger.debug(f"{user_id=}")
        room_alias = options['room_alias']
        logger.debug(f"{room_alias=}")
        room_name = options['room_name']
        room_subject = options['room_subject']
        greeting = options['greeting']
        resp = None
        try:
            loop = asyncio.get_event_loop()
            resp = loop.run_until_complete(
                main(
                    user_id,
                    room_alias=room_alias,
                    room_name=room_name,
                    room_subject=room_subject,
                    greeting=greeting,
                )
            )
            logger.debug(resp)
        except KeyboardInterrupt:
            pass
        self.stdout.write(
            self.style.SUCCESS(f'Done testing Matrix bot {resp}')
        )