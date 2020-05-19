""" Create a Human object from SocialUser userid or screen_name """

from django.core.management.base import BaseCommand, CommandError

from moderation.models import Human
from moderation.models import SocialUser
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create Human objects all from SocialUser objects'
    
    def handle(self, *args, **options):
        count = 0
        for su in SocialUser.objects.all():
            created = False
            try:
                human = Human.objects.get(socialuser=su)
            except Human.DoesNotExist:
                logger.debug("Human does not exist...")
                try:
                    human = Human()
                    human.save()
                    human.socialuser.add(su)
                    human.save()
                    created = True
                except:
                    self.style.ERROR(f'A database error has occured.')
                    continue
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Done creating Human object {human}')
                )
                count += 1
            else:
                self.stdout.write(
                    self.style.ERROR(f'Human object {human} already exists.')
                )
        self.stdout.write(
            self.style.SUCCESS(f'Done. {count} Human object were created.')
        )