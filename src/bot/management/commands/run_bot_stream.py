from django.core.management.base import BaseCommand, CommandError

from bot.stream import main


class Command(BaseCommand):
    help = 'Run bot stream'
    
    def add_arguments(self, parser):
        parser.add_argument('community', type=str)
    
    def handle(self, *args, **options):
        try:
            community = options['community']
        except KeyError:
            community = None
        main(community)
        self.stdout.write(self.style.SUCCESS('Done launching {community} stream.'))