from django.core.management.base import BaseCommand, CommandError
from bot.tasks import handle_add_friends_to_socialusers

class Command(BaseCommand):
    help = 'Add friends of all active Accounts to SocialUser table'

    def handle(self, *args, **options):
        handle_add_friends_to_socialusers()
        self.stdout.write(self.style.SUCCESS('Done'))