import simplejson as json
import uuid
import requests
from requests.exceptions import HTTPError
from decimal import Decimal
import logging

from silver.models.documents.invoice import Invoice
from silver.models.documents.entries import DocumentEntry
from silver.models.product_codes import ProductCode
from silver.models.billing_entities.customer import Customer as SilverCustomer
from silver.models.billing_entities.provider import Provider as SilverProvider
from customer.tasks import generate_pdf

from crowdfunding.models import ProjectInvestment, Project
from customer.models import Customer, Provider, Product
from django.db import IntegrityError, DatabaseError, transaction

logger = logging.getLogger(__name__)

def get_quantity(pledged=Decimal('0.0'), unit_price=Decimal('0.0')):
    if not unit_price:
        return 0
    return pledged/unit_price

def get_product_code_silver_id(product_code: str):
    try:
        return Product.objects.get(product_code=product_code).silver_id
    except Product.DoesNotExist:
        return

def create_silver_invoice(_uuid):
    #Create an invoice for corresponding ProjectInvestment
    try:
        pi = ProjectInvestment.objects.get(uuid=_uuid)
    except ProjectInvestment.DoesNotExist:
        return
    customer_instance = Customer.objects.filter(user=pi.user).first()
    logger.debug(f"{customer_instance=}")
    if not customer_instance:
        return
    try:
        provider_instance = pi.project.provider
        logger.debug(f"{provider_instance=}")
    except:
        return
    # check if invoice already exists
    invoice_qs = Invoice.objects.select_for_update().filter(id=pi.invoice)
    with transaction.atomic():
        try:
            invoice = invoice_qs[0]
            logger.debug(f"{invoice=}")
        except IndexError:
            logger.error(f"No Invoice object with id {pi.invoice}")
            return
        # if the Invoice already has an entry, return to avoid duplicate entries
        if invoice.entries:
            if not invoice.pdf:
                generate_pdf.apply_async(args=(invoice.id, 'invoice'))
            return {"silver_invoice_id": invoice.id}
        due_date = pi.datetime.strftime("%Y-%m-%d")
        customer = SilverCustomer.objects.get(id=customer_instance.silver_id)
        provider = SilverProvider.objects.get(id=provider_instance.silver_id)
        product_instance = pi.project.product
        logger.debug(f"product_code:{product_instance.product_code}")
        quantity = get_quantity(pledged=pi.pledged, unit_price=product_instance.unit_price)
        invoice.currency='EUR'
        invoice.transaction_currency='EUR'
        invoice.due_date = due_date
        invoice.issue_date = due_date
        invoice.customer = customer
        invoice.provide = provider
        invoice.sales_tax_percent = product_instance.sales_tax_percent
        invoice.sales_tax_name = product_instance.sales_tax_name
        invoice.currency = product_instance.currency
        invoice.state = 'draft'
        invoice.save()

    if create_invoice_entry(
        pk=invoice.id,
        description=product_instance.description,
        unit=product_instance.unit,
        quantity=quantity,
        unit_price=product_instance.unit_price,
        product_code=product_instance.product_code,
        date=due_date
    ):
        if (issue_silver_invoice(
                id=invoice.id,
                issue_date=due_date
            )):
            if (pay_silver_invoice(
                id=invoice.id,
                paid_date=due_date
            )):
                generate_pdf.apply_async(args=(invoice.id, 'invoice'))
                return {"silver_invoice_id": invoice.id}

def create_invoice_entry(
        pk, # Silver.Invoice.id
        description,
        unit,
        quantity,
        unit_price,
        product_code,
        date    
    ):
    try:
        product_code_instance = ProductCode.objects.get(value=product_code)
    except ProductCode.DoesNotExist:
        logger.error(
            f"ProductCode with value={product_code} does not exist"
        )
        return
    try:
        invoice = Invoice.objects.get(id=pk)
    except Invoice.DoesNotExist:
        logger.error(f"Invoice with id={pk} does not exist.")
        return
    try:
        doc_entry = DocumentEntry.objects.create(
            description=description,
            unit=unit,
            quantity=quantity,
            unit_price=unit_price,
            product_code=product_code_instance,
            start_date=date,
            end_date=date,
            prorated=False,
            invoice=invoice,
        )
        logger.debug(f"{doc_entry=}")
        return True
    except DatabaseError as e:
        logger.error(f"Error during creation of DocumentEntry: {e}")
        return

def issue_silver_invoice(id, issue_date):
    try:
        invoice = Invoice.objects.get(id=id)
    except Invoice.DoesNotExist:
        return False
    invoice.issue(issue_date=issue_date)
    return True

def pay_silver_invoice(id, paid_date):
    try:
        invoice = Invoice.objects.get(id=id)
    except Invoice.DoesNotExist:
        return False
    invoice.pay(paid_date=paid_date)
    return True