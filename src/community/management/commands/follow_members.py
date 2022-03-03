import logging
from django.core.management.base import  BaseCommand, CommandError
from bot.bin.friendship import create_friendship_members
from community.models import Community
from moderation.social import get_socialuser_from_screen_name

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Find replies through Twitter API search'
    def add_arguments(self, parser):
        parser.add_argument('community', type=str)
        parser.add_argument('--users', type=int)
        parser.add_argument('--friends', type=str)
        parser.add_argument('--followers', type=str)
        parser.add_argument(
            '--prospects',
            dest='prospects',
            action='store_true',
            help="include active Prospects for this community"
        )

    def handle(self, *args, **options):
        community_name = options["community"]
        users = options["users"] or 400
        friends_sn = options["friends"]
        followers_sn = options["followers"]
        logger.info(options["prospects"])
        if friends_sn:
            friends_of = get_socialuser_from_screen_name(friends_sn)
        else:
            friends_of = None
        if followers_sn:
            followers_of = get_socialuser_from_screen_name(followers_sn)
        else:
            followers_of = None
        logger.info(followers_of)
        logger.info(friends_of)
        try:
            community = Community.objects.get(name=community_name)
        except Community.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"'{community_name}' does not exist."
                )
            )
            return
        create_friendship_members(
            community,
            users=users,
            friends_of=friends_of,
            followers_of=followers_of,
            prospects=options["prospects"],  
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Done."
            )
        )