import logging
import requests
import re
import json
from urllib.parse import urlparse
from requests.exceptions import HTTPError

from django.db.models.signals import post_save
from django.db import DatabaseError
from django.dispatch import receiver
from django.test import Client

from silver.models.billing_entities.customer import Customer as SilverCustomer
from silver.models.billing_entities.provider import Provider as SilverProvider
from customer.tasks import handle_create_customer_and_draft_invoice
from customer.models import Customer, Provider, Product
from customer.silver import create_customer_and_draft_invoice
from crowdfunding.models import ProjectInvestment
from silver.models import ProductCode

logger = logging.getLogger(__name__)

@receiver(post_save, sender=ProjectInvestment)
def create_customer_and_draft_invoice_receiver(sender, instance, created, **kwargs):
    # start invoicing only if instance is paid
    # start invoicing only if instance doesn't already have invoice
    if instance.paid and not instance.invoice:
        logger.debug(
            f"create_customer_and_draft_invoice() for {instance=}"
        )
        create_customer_and_draft_invoice(instance)

@receiver(post_save, sender=Customer)
def on_customer_update(sender, instance, created, **kwargs):
    if not customer_instance_is_complete(instance):
        return
    if created:
        return
    if instance.silver_id is not None:
        update_silver_customer(instance)
    else:
        create_silver_customer(instance)

def customer_instance_is_complete(instance):
    is_complete = (
        instance.user and
        instance.first_name and
        instance.last_name and
        #instance.company and
        #instance.email and
        instance.address_1 and
        instance.country and
        instance.city and
        instance.zip_code
    )
    return is_complete

def create_silver_customer(instance):
    try:
        sc= SilverCustomer.create(
            first_name = instance.first_name,
            last_name = instance.last_name,
            #payment_due_days =
            consolidated_billing = False,
            customer_reference = str(instance.user.id),
            #sales_tax_number =
            sales_tax_percent = 0,
            #sales_tax_name =
            #currency =
            company = instance.company,
            address_1 = instance.address_1,
            address_2 = instance.address_2,
            country = instance.country,
            #phone = models.CharField(max_length=32, blank=True, null=True)
            email = instance.email,
            city = instance.city,
            state = instance.state,
            zip_code = str(instance.zip_code),
            #extra = 
        )
        logger.debug(f'Silver Customer: {sc} creation was successful!')
    except:
        pass
    else:
        Customer.objects.filter(id=instance.id).update(silver_id=sc.id)

def update_silver_customer(instance):
    try:
        SilverCustomer.objects.filter(pk=instance.id).update(
            first_name = instance.first_name,
            last_name = instance.last_name,
            #payment_due_days =
            #consolidated_billing = False,
            #customer_reference = str(instance.user.id),
            #sales_tax_number =
            #sales_tax_percent = 0,
            #sales_tax_name =
            #currency =
            company = instance.company,
            address_1 = instance.address_1,
            address_2 = instance.address_2,
            country = instance.country,
            #phone = models.CharField(max_length=32, blank=True, null=True)
            email = instance.email,
            city = instance.city,
            state = instance.state,
            zip_code = str(instance.zip_code),
            #extra = 
        )
        sc = SilverCustomer.objects.get(id=instance.id)
        logger.debug(f'Silver Customer: {sc} update was successful!')
    except:
        pass

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
    try:
        sp = SilverProvider.objects.create(
            name = instance.name,
            flow = instance.flow,
            company = instance.company,
            email = instance.email,
            address_1 = instance.address_1,
            address_2 = instance.address_2,
            country = instance.country,
            city = instance.city,
            state = instance.state,
            zip_code = str(instance.zip_code),
            extra = instance.extra,
            invoice_series = instance.invoice_series,
            invoice_starting_number = instance.invoice_starting_number,
            proforma_series = instance.proformar_series,
            proforma_starting_number = instance.proforma_starting_number,
            default_document_state = instance.default_document_state,
            meta = instance.meta,
        )
    except:
        pass
    else:
        Provider.objects.filter(id=instance.id).update(silver_id=sp.id)

def update_silver_provider(instance):
    logger.debug('*****')
    try:
        SilverProvider.objects.filter(id=instance.silver_id).update(
            name = instance.name,
            flow = instance.flow,
            company = instance.company,
            email = instance.email,
            address_1 = instance.address_1,
            address_2 = instance.address_2,
            country = instance.country,
            city = instance.city,
            state = instance.state,
            zip_code = str(instance.zip_code),
            extra = instance.extra,
            invoice_series = instance.invoice_series,
            invoice_starting_number = instance.invoice_starting_number,
            proforma_series = instance.proforma_series,
            proforma_starting_number = instance.proforma_starting_number,
            default_document_state = instance.default_document_state,
            meta = instance.meta,
        )
    except DatabaseError as e:
        logger.error(e)

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
    try:
        pc = ProductCode.objects.create(
            value = instance.product_code
        )
    except:
        pass
    else:
        Product.objects.filter(pk=instance.pk).update(silver_id=pc.id)

def update_silver_product_code(instance):
    try:
        ProductCode.objects.filter(
            id = instance.silver_id
        ).update(value=instance.product_code)
    except:
        pass

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