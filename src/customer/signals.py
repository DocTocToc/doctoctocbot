import logging
import requests
from requests.exceptions import HTTPError
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.utils import DatabaseError
from django.conf import settings

from crowdfunding.models import ProjectInvestment
from customer.models import Customer, Provider

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

def copper_provider_json(instance):
    """Create a dictionary containing all the values of the Provider instance"""
    data = dict()
    keys = [
        "name",
        "company",
        "email",
        "address_1",
        "address_2",
        "country",
        "city",
        "state",
        "zip_code",
        "extra",
        "flow",
        "invoice_series",
        "invoice_starting_number",
        "proforma_series",
        "proforma_starting_number",
        "default_document_state",
        "meta",
    ]
    for key in keys:
        d = {key: getattr(instance, key, None)}
        data.update(d)
    return data
        
def create_copper_provider(instance):
    if not settings.COPPER_TOKEN:
        logger.warn("To use Copper, you must set COPPER_TOKEN in your .env file.")
        return
    authorization = f"Token {settings.COPPER_TOKEN}"
    if settings.DEBUG:
        protocol="http://"
    else:
        protocol="https://"
    API_ENDPOINT = f"{protocol}{settings.COPPER_URL}/providers/"
    data = copper_provider_json(instance)
    headers = {
        'content-type': 'application/json',
        'Authorization': authorization,    
    }
    try:
        response = requests.post(url=API_ENDPOINT, data=json.dumps(data), headers=headers)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
        logger.debug(f"{response} \n {response.text} \n id:{json.loads(response.text)['id']}")
        if response.ok:
            copper_provider_id=int(json.loads(response.text)['id'])
            Provider.objects.filter(pk=instance.pk).update(copper_provider_id=copper_provider_id)
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
    else:
        logger.info(f'Provider {instance.company} creation was successful!')

def update_copper_provider(instance):
    if not settings.COPPER_TOKEN:
        logger.warn("To use Copper, you must set COPPER_TOKEN in your .env file.")
        return
    copper_provider_id = instance.copper_provider_id
    if not copper_provider_id:
        logger.warn(
            "This instance does not have a Copper provider id."
            "It cannot be updated on Copper."    
        )
        return        
    authorization = f"Token {settings.COPPER_TOKEN}"
    if settings.DEBUG:
        protocol="http://"
    else:
        protocol="https://"
    API_ENDPOINT = f"{protocol}{settings.COPPER_URL}/providers/{copper_provider_id}/"
    data = copper_provider_json(instance)
    headers = {
        'content-type': 'application/json',
        'Authorization': authorization,    
    }
    try:
        response = requests.put(url=API_ENDPOINT, data=json.dumps(data), headers=headers)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
    else:
        logger.info(f'Provider {instance.company} was successfully updated!')

@receiver(post_save, sender=Provider)
def create_update_copper_provider(sender, instance, created, **kwargs):
    """ Create or update provider in Silver billing app.
    Silver is called copper inside our code.
    Create a new provider or update an existing provider.
    """
    if not provider_instance_is_complete(instance):
        logger.warn(
            "Required fields are missing in Provider instance. "
            f"Provider will not be {(lambda: 'modified', lambda: 'created')[created]()} on Copper."
        )
        return
    if created is True:
        create_copper_provider(instance)
    else:
        update_copper_provider(instance)


def provider_instance_is_complete(instance):
    is_complete = (
        instance.name and
        instance.company and
        instance.email and
        instance.address_1 and
        instance.country and
        instance.city and
        instance.zip_code and
        instance.invoice_series and 
        instance.invoice_starting_number and
        instance.proforma_series and 
        instance.proforma_starting_number
    )
    return is_complete