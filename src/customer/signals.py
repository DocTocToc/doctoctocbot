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

from customer.copper import get_headers, get_api_endpoint

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

@receiver(post_save, sender=Customer)
def on_customer_update(sender, instance, created, **kwargs):
    if not customer_instance_is_complete(instance):
        return
    if created:
        return
    if instance.copper_id:
        update_copper_customer(instance)
    else:
        create_copper_customer(instance)

def customer_instance_is_complete(instance):
    is_complete = (
        instance.user and
        instance.first_name and
        instance.last_name and
        #instance.company and
        instance.email and
        instance.address_1 and
        instance.country and
        instance.city and
        instance.zip_code
    )
    return is_complete

def create_copper_customer(instance):
    data = json.dumps(copper_customer_json(instance))
    logger.debug(get_api_endpoint("customers"))
    logger.debug(get_headers())
    logger.debug(data)
    try:
        response = requests.post(
            url=get_api_endpoint("customers"),
            data=data,
            headers=get_headers()
        )
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
        logger.debug(f"{response} \n {response.text} \n id:{json.loads(response.text)['id']}")
        if response.ok:
            copper_customer_id=int(json.loads(response.text)['id'])
            Customer.objects.filter(pk=instance.pk).update(copper_id=copper_customer_id)
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
    else:
        logger.info(f'Provider {instance.last_name} creation was successful!')

def update_copper_customer(instance):
    copper_customer_id = instance.copper_id
    if not copper_customer_id:
        logger.warn(
            "This instance does not have a Copper customer id."
            "It cannot be updated on Copper."    
        )
        return
    data = json.dumps(copper_customer_json(instance))
    try:
        response = requests.put(
            url=get_api_endpoint("customers", copper_customer_id),
            data=data,
            headers=get_headers()
        )
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
        logger.debug(f"{response} \n {response.text} \n id:{json.loads(response.text)['id']}")
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
    else:
        logger.info(f'Provider {instance.last_name} creation was successful!')

def copper_customer_json(instance):
    """Create a dictionary containing all the values of the Customer instance"""
    data = dict()
    keys = [
        "customer_reference",
        "first_name",
        "last_name",
        "company",
        "email",
        "address_1",
        "address_2",
        "country",
        "city",
        "state",
        "zip_code",
        "extra",
        "sales_tax_percent",
        "sales_tax_name",
        "sales_tax_number",
        "consolidated_billing"
    ]
    for key in keys:
        d = {key: getattr(instance, key, "")}
        data.update(d)
    data.update({"customer_reference": instance.user.id})
    data.update({"sales_tax_percent": 0})
    data.update({"consolidated_billing": False})
    return data

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
    data = json.dumps(copper_provider_json(instance))
    try:
        response = requests.post(
            url=get_api_endpoint("providers"),
            data=data,
            headers=get_headers()
        )
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
        logger.debug(f"{response} \n {response.text} \n id:{json.loads(response.text)['id']}")
        if response.ok:
            copper_id=int(json.loads(response.text)['id'])
            Provider.objects.filter(pk=instance.pk).update(copper_id=copper_id)
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
    else:
        logger.info(f'Provider {instance.company} creation was successful!')

def update_copper_provider(instance):
    copper_id = instance.copper_id
    if not copper_id:
        logger.warn(
            "This instance does not have a Copper provider id."
            "It cannot be updated on Copper."    
        )
        return        
    data = json.dumps(copper_provider_json(instance))

    try:
        response = requests.put(
            url=get_api_endpoint("providers", copper_id),
            data=data,
            headers=get_headers()
        )
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
