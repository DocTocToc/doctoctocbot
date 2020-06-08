from django.core.management.base import BaseCommand, CommandError
import logging

from dm.retrieve import savedm


class Command(BaseCommand):
    help = 'Retrieve direct messages, update DirectMessage table'
    
    def handle(self, *args, **options):
        savedm()
        self.stdout.write(self.style.SUCCESS('Done retrieving DMs.'))