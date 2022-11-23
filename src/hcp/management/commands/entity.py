import logging
from django.core.management.base import BaseCommand, CommandError
from hcp.models import HealthCareProvider
from moderation.models import Entity
from django.db import DatabaseError
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Link HealthCareProvider objects to Entity objects'

    def add_arguments(self, parser):
        pass


    def add_entity(self, hcp: HealthCareProvider, entity: Entity):
        hcp.entity = entity
        hcp.save()
        self.count+=1
        human = hcp.human
        for socialuser in human.socialuser.all():
            if not socialuser.entity:
                socialuser.entity=entity
                socialuser.save()
        for djangouser in human.djangouser.all():
            if not djangouser.entity:
                djangouser.entity=entity
                djangouser.save()

    def handle(self, *args, **options):
        self.count = 0
        for hcp in HealthCareProvider.objects.filter(entity=None):
            entity = None
            human = hcp.human
            for socialuser in human.socialuser.all():
                if socialuser.entity:
                    entity = socialuser.entity
                    break
            for djangouser in human.djangouser.all():
                if djangouser.entity:
                    entity = djangouser.entity
                    break
            if not entity:
                try:
                    entity = Entity.objects.create()
                except DatabaseError:
                    continue
            self.add_entity(hcp, entity)
        self.stdout.write(
            self.style.SUCCESS(
                f'{self.count} {"entities" if self.count>1 else "entity"} added.'
            )
        )
