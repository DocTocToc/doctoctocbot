from django.core.management.base import  BaseCommand, CommandError
from moderation.profile import create_social_user_and_profile
from community.models import Community
from moderation.models import Follower
from community.helpers import get_community_bot_socialuser

class Command(BaseCommand):
    help = 'Add all followers of the bot of this community to SocialUser table'
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
        bot_su = get_community_bot_socialuser(community)
        if not bot_su:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Error. Could not get {community_name}'s bot SocialUser"
                    " instance."
                )
            )
            return
        bot_follower_id = Follower.objects.filter(user=bot_su).latest().id_list
        n = 0
        for userid in bot_follower_id:
            created = create_social_user_and_profile(userid)
            if created:
                n+=1
        self.stdout.write(
            self.style.SUCCESS(
                "Done. "
                f"{n} new SocialUser instance{'s' if n>1 else ''}) created."
            )
        )