from django.core.management.base import BaseCommand, CommandError

from bot.stream import main


class Command(BaseCommand):
    help = 'Run bot stream'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'community',
            nargs='?',
            type=str
        )
    
    def handle(self, *args, **options):
        community = options['community']
        if not community:
            self.stdout.write(
                self.style.SUCCESS(
                    f"'community' argument is not set. Exiting."
                )
            )
            return
        main(community)
        self.stdout.write(self.style.SUCCESS(f'Done launching {community} stream.'))