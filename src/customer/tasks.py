import logging
logger = logging.getLogger(__name__)
from django.utils.translation import activate
from silver.models import BillingDocumentBase
from customer.models import Customer
from silver.models.documents.invoice import Invoice
from celery import shared_task
from celery_once import QueueOnce
from django.conf import settings
from crowdfunding.models import ProjectInvestment
from customer.silver import create_customer_and_draft_invoice

PDF_GENERATION_TIME_LIMIT = getattr(
    settings,
    'PDF_GENERATION_TIME_LIMIT',
    60
)  # default 60s

@shared_task(base=QueueOnce, once={'graceful': True},
             time_limit=PDF_GENERATION_TIME_LIMIT)
def generate_pdf(document_id, document_type):
    document = BillingDocumentBase.objects.get(
        id=document_id,
        kind=document_type
    )
    try:
        customer = Customer.objects.get(silver_id=document.customer.id)
        logger.debug(f'{customer.language=}')
        activate(customer.language)
    except Customer.DoesNotExist:
        pass
    document.generate_pdf()
    invoice = Invoice.objects.get(id=document_id)
    logger.debug("invoice.pdf: {invoice.pdf}")
    if invoice.pdf:
        try:
            pi = ProjectInvestment.objects.get(invoice=document_id)
        except ProjectInvestment.DoesNotExist:
            return
        pi.invoice_pdf = True
        pi.save()

@shared_task
def handle_create_customer_and_draft_invoice(uuid):
    try:
        instance = ProjectInvestment.objects.get(uuid=uuid)
    except ProjectInvestment.DoesNotExist:
        return
    create_customer_and_draft_invoice(instance)