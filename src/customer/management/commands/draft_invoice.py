# -*- coding: utf-8 -*-
"""Create draft invoices

This management command creates draft Sivler invoices from the content of
the ProjectInvestment table.
When they invested, users didn't add their first names, last names, addresses
and other data required in an invoice.
We create draft invoices with empty fields that will be updated when users fill
out their billing information.
"""

from django.core.management.base import BaseCommand, CommandError

from crowdfunding.models import ProjectInvestment


class Command(BaseCommand):
    help = 'Create draft invoices from ProjectInvestment objects.'
    
    def handle(self, *args, **options):
        #
        #
        #
        self.stdout.write(self.style.SUCCESS('Draft invoices created.'))