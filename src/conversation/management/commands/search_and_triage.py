from django.core.management.base import  BaseCommand, CommandError
from bot.doctoctocbot import main as search_and_triage


class Command(BaseCommand):
    help = 'Search all status with # with Twitter search API and reprocess them to add tree roots'
    
    def handle(self, *args, **options):
        search_and_triage()
        self.stdout.write(self.style.SUCCESS('Searched tweets and added tree roots.'))