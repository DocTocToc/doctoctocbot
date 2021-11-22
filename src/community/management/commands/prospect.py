from django.core.management.base import  BaseCommand, CommandError
from community.prospect import Prospect
from moderation.models import SocialUser, Category
from community.models import Community


class Command(BaseCommand):
    help = 'Prospect new members for a community'
    def add_arguments(self, parser):
        parser.add_argument(
            'community',
            type=str,
            help='Community to prospect for')
        parser.add_argument(
            '--category',
            type=str,
            help='Which category of users are we looking for?'
        )
        parser.add_argument(
            '--follower',
            type=int,
            help='Min number of followers for user to be added to prospects'
        )
        parser.add_argument(
            '--friend',
            type=int,
            help='Min number of friends for user to be added to prospects'  
        )
        parser.add_argument(
            '--cache',
            type=int,
            help='Update relationship data if more than cache days old'  
        )
        parser.add_argument(
            '--most_common',
            type=int,
            help='Most common to display'  
        )
        parser.add_argument(
            '--update',
            dest='update_network',
            action='store_true',
            help='add this flag to update the network (followers and friends)'
        )

    def handle(self, *args, **options):
        community_name = options["community"]
        category_name = options["category"]
        friend = options["friend"]
        follower = options["follower"]
        cache = options["cache"]
        update_network: bool = options["update_network"]
        most_common = options["most_common"]

        try:
            community = Community.objects.get(name=community_name)
        except Community.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"Community '{community_name}' does not exist."
                )
            )
            return
        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"Category '{category_name}' does not exist."
                )
            )
            return

        p = Prospect(
            community=community,
            category=category,
            min_follower=follower,
            min_friend=friend,
            network_cache = cache,
            most_common = most_common
        )
        if update_network:
            p.update_network()

        p.friends=p.get_friends()
        p.followers=p.get_followers()
        p.add_social_users(
            friends=p.min_friend,
            followers=p.min_follower    
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'{p.display()}'
            )
        )