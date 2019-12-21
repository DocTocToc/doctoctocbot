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
from customer.silver import get_api_endpoint, get_headers

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
    
"""    
def create_silver_invoice(uuid):
    #Create an invoice for corresponding ProjectInvestment
    try:
        pi = ProjectInvestment.objects.get(pk=uuid)
    except ProjectInvestment.DoesNotExist:
        return
    customer_instance = Customer.objects.filter(user=pi.user).first()
    if not customer_instance:
        return
    try:
        provider_instance = pi.project.provider
    except:
        return
    
    # check if invoice already exists
    invoice_id = pi.invoice
    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        invoice =None
        
    if invoice:
        due_date = pi.datetime.strftime("%Y-%m-%d")
        customer = get_api_endpoint("customers", customer_instance.silver_id )
        provider = get_api_endpoint("providers", provider_instance.silver_id )
        product_instance = pi.project.product
        logger.debug(f"product_code:{product_instance.product_code}")
        quantity = get_quantity(pledged=pi.pledged, unit_price=product_instance.unit_price)
        invoice_dct = {
            "due_date": due_date,
            "issue_date": due_date,
            "customer": customer,
            "provider": provider,
            "sales_tax_percent": product_instance.sales_tax_percent,
            "sales_tax_name": product_instance.sales_tax_name,
            "currency": product_instance.currency,
            "state": "draft"
        }
        
        data = json.dumps(invoice_dct)
        logger.debug(f"data: {data}")
        try:
            response = requests.patch(
                url=get_api_endpoint("invoices", invoice_id),
                data=data,
                headers=get_headers()
            )
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
            logger.debug(f"{response} \n {response.text} \n id:{json.loads(response.text)['id']}")
            if response.ok:
                invoice_id=int(json.loads(response.text)['id'])
                ProjectInvestment.objects.filter(pk=pi.pk).update(invoice=invoice_id)
                ok = False
                if create_invoice_entry(
                    pk=invoice_id,
                    description=product_instance.description,
                    unit=product_instance.unit,
                    quantity=quantity,
                    unit_price=product_instance.unit_price,
                    product_code=product_instance.product_code,
                    date=due_date
                ):
                    if (issue_silver_invoice(
                            id=invoice_id,
                            issue_date=due_date
                        )):
                        if (pay_silver_invoice(
                            id=invoice_id,
                            paid_date=due_date
                        )):
                            generate_pdf.apply_async(args=(invoice_id, 'invoice'))
                            return {"silver_invoice_id": invoice_id}
        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err}')
        except Exception as err:
            logger.error(f'Other error occurred: {err}')
        else:
            logger.info(f'Invoice {invoice_id} creation was successful!')
"""
 
def create_silver_invoice(uuid):
    #Create an invoice for corresponding ProjectInvestment
    try:
        pi = ProjectInvestment.objects.get(pk=uuid)
    except ProjectInvestment.DoesNotExist:
        return
    customer_instance = Customer.objects.filter(user=pi.user).first()
    if not customer_instance:
        return
    try:
        provider_instance = pi.project.provider
    except:
        return
    # check if invoice already exists
    try:
        invoice = Invoice.objects.get(id=pi.invoice)
    except Invoice.DoesNotExist:
        return
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
        pk,
        description,
        unit,
        quantity,
        unit_price,
        product_code,
        date    
    ):
    invoice_entry_dct = {
        "description": description,
        "unit": unit,
        "quantity": quantity,
        "unit_price": unit_price,
        "product_code": None,
        "start_date": date,
        "end_date": date,
        "prorated": False
    }
    data = json.dumps(invoice_entry_dct)
    logger.debug(f"data: {data}")
    try:
        response = requests.post(
            url=f"{get_api_endpoint('invoices', pk)}entries/",
            data=data,
            headers=get_headers()
        )
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
        logger.debug(f"{response} \n {response.text} \n")
        if response.ok:
            entry_id=int(json.loads(response.text)['id'])
            try:
                entry = DocumentEntry.objects.get(id=entry_id)
            except DocumentEntry.DoesNotExist:
                return
            if not entry.product_code:
                try:
                    product_code_instance = ProductCode.objects.get(value=product_code)
                except ProductCode.DoesNotExist:
                    return
                entry.product_code=product_code_instance
                entry.save()
                return True
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
    else:
        logger.info(f'Invoice entry creation was successful!')

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
    
"""
def issue_silver_invoice(id, issue_date):
    issue_dct = {
        "state": "issued",
        "issue_date": issue_date,
    }
    data = json.dumps(issue_dct)
    try:
        response = requests.patch(
            url=f"{get_api_endpoint('invoices', id)}state/",
            data=data,
            headers=get_headers()
        )
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
        logger.debug(f"{response} \n {response.text} \n")
        if response.ok:
            generate_pdf.apply_async(args=(id, 'invoice'))
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
    else:
        logger.info(f'Invoice entry creation was successful!')
    """