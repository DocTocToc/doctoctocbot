import logging
import requests
import re
from requests.exceptions import HTTPError
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.utils import DatabaseError
from django.conf import settings
from urllib.parse import urlparse

from crowdfunding.models import ProjectInvestment
from customer.models import Customer, Provider, Product

from customer.silver import get_headers, get_api_endpoint

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
    if instance.silver_id:
        update_silver_customer(instance)
    else:
        create_silver_customer(instance)

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

def create_silver_customer(instance):
    data = json.dumps(silver_customer_json(instance))
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
            silver_customer_id=int(json.loads(response.text)['id'])
            Customer.objects.filter(pk=instance.pk).update(silver_id=silver_customer_id)
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
    else:
        logger.info(f'Customer {instance.last_name} creation was successful!')

def update_silver_customer(instance):
    silver_customer_id = instance.silver_id
    if not silver_customer_id:
        logger.warn(
            "This instance does not have a Copper customer id."
            "It cannot be updated on Copper."    
        )
        return
    data = json.dumps(silver_customer_json(instance))
    try:
        response = requests.put(
            url=get_api_endpoint("customers", silver_customer_id),
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

def silver_customer_json(instance):
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

def silver_provider_json(instance):
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

def create_silver_provider(instance):
    data = json.dumps(silver_provider_json(instance))
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
            silver_id=int(json.loads(response.text)['id'])
            Provider.objects.filter(pk=instance.pk).update(silver_id=silver_id)
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
    else:
        logger.info(f'Provider {instance.company} creation was successful!')

def update_silver_provider(instance):
    silver_id = instance.silver_id
    if not silver_id:
        logger.warn(
            "This instance does not have a Copper provider id."
            "It cannot be updated on Copper."    
        )
        return        
    data = json.dumps(silver_provider_json(instance))

    try:
        response = requests.put(
            url=get_api_endpoint("providers", silver_id),
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
def create_update_silver_provider(sender, instance, created, **kwargs):
    """ Create or update provider in Silver billing app.
    Create a new provider or update an existing provider.
    """
    if not provider_instance_is_complete(instance):
        logger.warn(
            "Required fields are missing in Provider instance. "
            f"Provider will not be {(lambda: 'modified', lambda: 'created')[created]()} on Copper."
        )
        return
    if created is True:
        create_silver_provider(instance)
    else:
        update_silver_provider(instance)


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

def create_silver_product_code(instance):
    data = json.dumps({"value": instance.product_code})
    try:
        response = requests.post(
            url=get_api_endpoint("product-codes"),
            data=data,
            headers=get_headers()
        )
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
        logger.debug(f"{response}\n {response.text}\n {json.loads(response.text)}\n")
        if response.ok:
            url = json.loads(response.text)['url']
            url_parsed = urlparse(url)
            path = url_parsed.path
            lst = re.findall('\d+', path)
            if not lst:
                return
            silver_id = int(lst[0])
            logger.debug(f"silver_id:{silver_id}")
            Product.objects.filter(pk=instance.pk).update(silver_id=silver_id)
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
    else:
        logger.info(f'Product {instance.product_code} creation was successful!')

def update_silver_product_code(instance):
    silver_id = instance.silver_id
    if not silver_id:
        logger.warn(
            "This instance does not have a Copper provider id."
            "It cannot be updated on Copper."    
        )
        return        
    data = json.dumps({"value": instance.product_code})
    try:
        response = requests.put(
            url=get_api_endpoint("product-codes", silver_id),
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
        logger.info(f'product_code {instance.product_code} was successfully updated!')

@receiver(post_save, sender=Product)
def create_update_silver_product_code(sender, instance, created, **kwargs):
    """ Create or update product_code in Silver billing app.
    Create a new product_code or update an existing product_code.
    """
    if not instance.product_code:
        logger.warn(
            "Required field 'product_code' is missing in Product instance. "
            f"product_code will not be {(lambda: 'modified', lambda: 'created')[created]()} on Copper."
        )
        return
    if created is True:
        create_silver_product_code(instance)
    else:
        update_silver_product_code(instance)