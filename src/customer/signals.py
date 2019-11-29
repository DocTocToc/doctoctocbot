import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.utils import DatabaseError

from crowdfunding.models import ProjectInvestment
from customer.models import Customer

logger = logging.getLogger(__name__)

@receiver(post_save, sender=ProjectInvestment)
def create_customer(sender, instance, created, **kwargs):
    logger.debug("create_customer()")
    if instance.paid is True:
        logger.debug("create_customer(), paid is True")
        try:
            Customer.objects.create(
                user = instance.user,
            )
        except DatabaseError:
            return
        