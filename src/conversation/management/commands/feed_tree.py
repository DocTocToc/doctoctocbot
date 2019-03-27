from django.core.management.base import BaseCommand, CommandError

from conversation.utils import feed_tree
from conversation.models import create_tree


class Command(BaseCommand):
    help = 'Feed tree \n Usage: feed_tree <statusid>'
    
    def add_arguments(self, parser):
        parser.add_argument('statusid', type=int)
        
    def handle(self, *args, **options):
        statusid = options['statusid']
        create_tree(statusid)
        feed_tree(statusid)
        self.stdout.write(self.style.SUCCESS('Tree fed.'))