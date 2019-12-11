import json
from decimal import Decimal
import logging
from crowdfunding.models import ProjectInvestment, Project
from customer.models import Customer, Provider
from customer.copper import get_api_endpoint, get_headers
import requests
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)

def create_invoice(uuid):
    """Create an invoice for corresponding ProjectInvestment
    """
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
    
    due_date = pi.datetime.strftime("%Y-%m-%d")
    customer = get_api_endpoint("customers", customer_instance.copper_id )
    provider = get_api_endpoint("providers", provider_instance.copper_id )
    product_instance = pi.project.product
    
    quantity = get_quantity(pledged=pi.pledged, unit_price=product_instance.unit_price)
    
    invoice_dct = {
        "due_date": due_date,
        "issue_date": due_date,
        "customer": customer,
        "provider": provider,
        "invoice_entries": [
            {
                "description": product_instance.description,
                "unit": product_instance.unit,
                "quantity": quantity,
                "unit_price": product_instance.unit_price,
                "product_code": product_instance.product_code,
                "start_date": due_date,
                "end_date": due_date,
                "prorated": False
            },
        ],
        "sales_tax_percent": product_instance.sales_tax_percent,
        "sales_tax_name": product_instance.sales_tax_name,
        "currency": product_instance.currency,
        "state": "draft"
    }
    
    data = json.dumps(invoice_dct)
    try:
        response = requests.post(
            url=get_api_endpoint("invoices"),
            data=data,
            headers=get_headers()
        )
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
        logger.debug(f"{response} \n {response.text} \n id:{json.loads(response.text)['id']}")
        if response.ok:
            invoice=int(json.loads(response.text)['id'])
            ProjectInvestment.objects.filter(pk=pi.pk).update(invoice=invoice)
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
    else:
        logger.info(f'Invoice {invoice} creation was successful!')

    def get_quantity(pledged=Decimal('0.0'), unit_price=Decimal('0.0')):
        if not unit_price:
            return 0
        return pledged/unit_price