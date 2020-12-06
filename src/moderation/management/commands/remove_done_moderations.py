"""
Remove moderations where the user was already categorized (except self mod).
"""

from django.core.management.base import BaseCommand, CommandError
from moderation.moderate import remove_done_moderations
from community.models import Community


class Command(BaseCommand):
    help = (
    'Remove moderations from this community where the user was already '
    'moderated.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '-com',
            '--community',
            nargs='?',
            type=str,
            help='Indicates the community these changes should be applied to'
        )

    def handle(self, *args, **kwargs):
        community_name = kwargs['community']
        try:
            Community.objects.get(name=community_name)
        except Community.DoesNotExist:
            self.stdout.write(self.style.ERROR("This community does not exist."))
            return       
        counter = remove_done_moderations(community_name)
        self.stdout.write(
            self.style.SUCCESS(
                f"{counter} moderations(s) were deleted. :)"
            )
        )