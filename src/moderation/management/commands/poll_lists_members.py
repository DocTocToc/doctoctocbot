from django.core.management.base import BaseCommand, CommandError

from moderation.lists.poll import poll_lists_members


class Command(BaseCommand):
    help = ("Poll lists of Twitter account, download their members, "
            "update UserModerationRelationship table")
    
    def handle(self, *args, **options):
        poll_lists_members()
        self.stdout.write(self.style.SUCCESS('Done polling lists members'))