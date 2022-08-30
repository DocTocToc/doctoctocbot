from django.core.management.base import  BaseCommand, CommandError
from django.conf import settings
from community.models import Community, Retweet
import hashlib
import os
from bot.tweepy_api import get_api
from bot.bin.search import search_triage
import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run bot search with API v2 and retweet

    def add_arguments(self, parser):
        parser.add_argument('community', type=str)
    
    def handle(self, *args, **options):
        try:
            community_str = options['community']
        except KeyError:
            return
        try:
            community = Community.objects.get(name=community_str)
        except Community.DoesNotExist:
            return
        search_triage(community)
        self.stdout.write(self.style.SUCCESS('Done searching & retweeting.'))