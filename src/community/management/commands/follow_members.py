from django.core.management.base import  BaseCommand, CommandError
from bot.bin.friendship import create_friendship_members
from community.models import Community


class Command(BaseCommand):
    help = 'Find replies through Twitter API search'
    def add_arguments(self, parser):
        parser.add_argument('community', type=str)
        parser.add_argument('--users', type=int)

    def handle(self, *args, **options):
        community_name = options["community"]
        users = options["users"] or 400
        try:
            community = Community.objects.get(name=community_name)
        except Community.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"'{community_name}' does not exist."
                )
            )
            return
        create_friendship_members(community, users=users)
        self.stdout.write(
            self.style.SUCCESS(
                "Done."
            )
        )