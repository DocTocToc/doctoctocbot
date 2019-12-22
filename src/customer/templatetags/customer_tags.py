import logging
from django import template
from customer.models import Customer

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter(name='is_customer')
def is_customer(user):
    return Customer.objects.filter(user=user).exists()
