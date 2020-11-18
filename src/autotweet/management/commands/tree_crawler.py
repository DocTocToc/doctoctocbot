from django.core.management.base import BaseCommand, CommandError
from autotweet.tree import lookup_replies

class Command(BaseCommand):
    help = 'Crawl status for reply tree.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--community',
            help='name of the community'
        )
        parser.add_argument(
            '--max',
            type=int,
            help='Maximum number of statuses to lookup'
        )

    def handle(self, *args, **options):
        community_name = options['community']
        max = options['max']
        lookup_replies(community_name, maximum=max)