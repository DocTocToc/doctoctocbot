import logging
from typing import List
from django.core.management.base import BaseCommand, CommandError
from hcp.models import Taxonomy, HealthCareProvider
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = (
        'Return a list of Twitter screen_name(s) that belong to given '
        'specialty taxonomy'
    )
    def add_arguments(self, parser):
        parser.add_argument('taxonomy', type=int)

    def handle(self, *args, **options):
        taxonomy_pk = options['taxonomy']
        logger.debug(f"{type(taxonomy_pk)=}")
        if not taxonomy_pk:
            return
        
        try:
            taxonomy = Taxonomy.objects.get(pk=taxonomy_pk)
        except Taxonomy.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    'No Taxonomy object with pk = "%s"' % taxonomy_pk
                )
            )
        hcp_qs = HealthCareProvider.objects.filter(taxonomy=taxonomy)
        if not hcp_qs:
            self.stdout.write(
                self.style.ERROR(
                    'No healthcare providers belonging to %s' % taxonomy
                )
            )
            return
        specialty: List = []
        for hcp in hcp_qs:
            su = hcp.human.socialuser.all().last()
            screen_name = su.screen_name_tag()
            if screen_name:
                specialty.append(f'@{screen_name}')
        specialty_str = ' '.join(specialty)
        self.stdout.write(self.style.SUCCESS(specialty_str))