""" Determine the main language of all SocialUser objects """

from django.core.management.base import BaseCommand, CommandError
from moderation.tasks import handle_all_socialuser_language

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Determine the main language of all SocialUser objects'

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--page",
            type=int,
            help="Number of elements per page."
        )

    def handle(self, *args, **options):
        per_page = options["page"]
        handle_all_socialuser_language(per_page)