from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from crowdfunding.models import ProjectInvestment
from crowdfunding.tasks import handle_add_campaign
from bot.tests.tweet import main
import logging

logger = logging.getLogger(__name__)

def count():
    total = ProjectInvestment.objects.count()
    if not total:
        return "Table ProjectInvestment is empty."
    has_campaign = ProjectInvestment.objects.filter(
        campaign__isnull=False
    ).count()
    has_campaign_percent = round(has_campaign/total*100)
    return (
        f'Total:{total}\n'
        f'Campaign set:{has_campaign} ({has_campaign_percent}%)\n'
        f'Campaign empty:{total-has_campaign} ({100-has_campaign_percent}%)\n'
    )


class Command(BaseCommand):
    help = "Add the correct Campaign field to all ProjectInvestment objects."
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(f'{count()}'))
        for pi in ProjectInvestment.objects.all():
            handle_add_campaign(str(pi.uuid))
        self.stdout.write(self.style.SUCCESS(f'{count()}'))