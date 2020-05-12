""" Create a Human object from SocialUser userid or screen_name """

from django.core.management.base import BaseCommand, CommandError

from moderation.models import Human
from moderation.social import get_socialuser
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create a Human object from SocialUser userid or screen_name'
    
    def add_arguments(self, parser):
        parser.add_argument('socialuser', type=str)
    
    def handle(self, *args, **options):
        socialuser =  options['socialuser']
        if not socialuser:
            self.stdout.write(self.style.ERROR('You must provide a username or a userid.'))
            return
        userid = None
        screen_name = None
        try:
            userid=int(socialuser)
        except ValueError:
            screen_name = socialuser
        if userid:
            su = get_socialuser(userid)
        elif screen_name:
            su = get_socialuser(screen_name)
        if not su:
            return
        logger.debug(su)
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
                return
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Done creating Human object {human}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'Human object {human} already exists.')
            )