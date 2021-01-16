from django.core.management.base import  BaseCommand, CommandError
from community.models import Community
from conversation.timeline import community_timeline

class Command(BaseCommand):
    help = """Add or update timeline tweets from members of a community to 
        database"""
    def add_arguments(self, parser):
        parser.add_argument('community', type=str)
        parser.add_argument('--users', type=int)

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
        community_timeline(community)
        self.stdout.write(
            self.style.SUCCESS(
                "Done."
            )
        )