from django.core.management.base import  BaseCommand, CommandError
from community.models import Community
from request.models import Queue
from request.utils import request_dm

class Command(BaseCommand):
    help = """Add or update timeline tweets from members of a community to 
        database"""
    def add_arguments(self, parser):
        parser.add_argument('community', type=str)

    def handle(self, *args, **options):
        community_name = options["community"]
        try:
            community = Community.objects.get(name=community_name)
        except Community.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"'{community_name}' does not exist."
                )
            )
            return
        if not community.twitter_request_dm:
            self.stdout.write(
                self.style.ERROR(
                    f"'{community_name}' does not allow request DM."
                )
            )
            return
        qs = Queue.objects.current.filter(
            state=Queue.PENDING,
            community=community,
            requestdm=None
        )
        count = qs.count()
        for q in qs:
            request_dm(q)
        self.stdout.write(
            self.style.SUCCESS(
                f"Done processing {count} queue(s)."
            )
        )