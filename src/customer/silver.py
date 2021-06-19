import logging
from django.conf import settings

from silver.models.billing_entities.customer import Customer as SilverCustomer
from silver.models.billing_entities.provider import Provider as SilverProvider
from silver.models.documents.invoice import Invoice as SilverInvoice
from crowdfunding.models import ProjectInvestment
from customer.models import Customer
from django.db.utils import DatabaseError, IntegrityError

import psycopg2

logger = logging.getLogger(__name__)

def get_protocol():
    if settings.DEBUG or settings.SILVER_IS_LOCAL:
        return "http://"
    else:
        return "https://"
    
def get_headers():
    assert settings.SILVER_TOKEN, "To use Silver, you must set SILVER_TOKEN in your .env file."
    authorization = f"Token {settings.SILVER_TOKEN}"
    return {
        'content-type': 'application/json',
        'Authorization': authorization,    
    }

def get_api_endpoint(endpoint: str, _id=None):
    if _id is None:
        _id = ""
    else:
        _id = f"{_id}/"
    return f"{get_protocol()}{settings.SILVER_URL}/{endpoint}/{_id}"

def create_customer_and_draft_invoice(instance):
    if instance.paid is True and instance.invoice is None:
        logger.debug("paid is True, invoice is None: create customer, silver customer (temp), silver invoice (draft)")
        try:
            doctocnet_customer, _created = Customer.objects.get_or_create(
                user = instance.user,
            )
        except DatabaseError:
            return
        try:
            silver_customer = SilverCustomer.objects.get(
                customer_reference=str(instance.user.id)
            )
        except SilverCustomer.DoesNotExist:
            silver_customer = create_draft_silver_customer(
                customer_reference = str(instance.user.id)
            )
        if not silver_customer:
            return
        # add silver_id to draft customer
        doctocnet_customer.silver_id = silver_customer.id
        # add email to draft customer
        email = instance.user.email
        if email:
            doctocnet_customer.email = email
        doctocnet_customer.save()
        project = instance.project
        if not project:
            logger.error(
                f"ProjectInvestment {instance} is not linked to any Project"
            )
            return
        provider = project.provider
        if not provider:
            logger.error(
                f"Project {instance.project} is not linked to any Provider"
            )
            return
        try:
            silver_provider = SilverProvider.objects.get(id=provider.silver_id)
        except SilverProvider.DoesNotExist:
            return
        #calculate ProjectInvestment cardinality
        cardinality = project_investment_cardinality(instance)
        logger.debug(f"{cardinality=}")
        try:
            silver_invoice = SilverInvoice.objects.create(
                customer=silver_customer,
                provider=silver_provider,
                number=cardinality,
            )
        except psycopg2.Error as e:
            logger.error(
                f"Silver invoice with {silver_customer=} {silver_provider=} "
                f"{cardinality=}  already exists. {e}"
            )
            try:
                silver_invoice= SilverInvoice.objects.get(
                    customer=silver_customer,
                    provider=silver_provider,
                    number=cardinality,
                )
                logger.warn(
                    f"{e} \n Silver invoice with {silver_customer=} "
                    f"{silver_provider=} {cardinality=}  already existed: "
                    f"{silver_invoice=}"
                )
            except SilverInvoice.DoesNotExist:
                return
        instance.invoice = silver_invoice.id
        instance.save()

def project_investment_cardinality(project_investment: ProjectInvestment):
    return ProjectInvestment.objects.filter(
        paid=True,
        datetime__lte=project_investment.datetime).count()

def create_draft_silver_customer(customer_reference: str):
    try:
        return SilverCustomer.objects.create(
            customer_reference = customer_reference,
            first_name = "?",
            last_name = "?",
            address_1 = "?",
            city = "?",
            country = "VA", # Holy See (Vatican City State)
        )
    except DatabaseError:
        return