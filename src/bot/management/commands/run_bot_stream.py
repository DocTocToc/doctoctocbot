from django.core.management.base import BaseCommand, CommandError

from bot.stream import main


class Command(BaseCommand):
    help = 'Polls lists of Twiter account, update UserModerationRelationship table'
    
    def handle(self, *args, **options):
        main()
        self.stdout.write(self.style.SUCCESS('Done launching stream.'))