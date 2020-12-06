from datetime import datetime

from django.core.management.base import  BaseCommand, CommandError

from conversation.tree.descendant import tree_search_crawl


class Command(BaseCommand):
    help = 'Find replies through Twitter API search'
    def add_arguments(self, parser):
        parser.add_argument('community', type=str)
        parser.add_argument('--days', type=int)

    def handle(self, *args, **options):
        community_name = options["community"]
        days = options["days"]
        self.stdout.write(
            self.style.NOTICE(
                f"tree_search_crawl('{community_name}', days={days}) "
                f"management command started at {datetime.utcnow()}."
            )
        )
        while True:
            ok = tree_search_crawl(community_name, days=days)
            if not ok:
                break
        self.stdout.write(
            self.style.ERROR(
                f"tree_search_crawl('{community_name}', days={days}) "
                f"management command stopped at {datetime.utcnow()}."
            )
        )