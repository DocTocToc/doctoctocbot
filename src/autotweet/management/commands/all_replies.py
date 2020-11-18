from django.core.management.base import BaseCommand, CommandError
from autotweet.tree import get_all_replies
from community.models import Community

class Command(BaseCommand):
    help = 'Crawl status for reply tree.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--community',
            help='name of the community'
        )

    def handle(self, *args, **options):
        community_name = options['community']
        try:
            community = Community.objects.get(name=community_name)
        except Community.DoesNotExist:
            return
        get_all_replies(community)