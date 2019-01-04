from django.core.management.base import  BaseCommand, CommandError
from conversation.utils import update_trees


class Command(BaseCommand):
    help = 'Update trees'
    
    def add_arguments(self, parser):
        parser.add_argument('hours', type=int)
        
    def handle(self, *args, **options):
        hours = options['hours']
        update_trees(hours)
        self.stdout.write(self.style.SUCCESS('Trees updated.'))