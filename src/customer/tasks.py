import logging
logger = logging.getLogger(__name__)
from silver.models import BillingDocumentBase
from silver.models.documents.invoice import Invoice
from celery import shared_task
from celery_once import QueueOnce
from django.conf import settings
from crowdfunding.models import ProjectInvestment

PDF_GENERATION_TIME_LIMIT = getattr(settings, 'PDF_GENERATION_TIME_LIMIT',
                                    60)  # default 60s

@shared_task(base=QueueOnce, once={'graceful': True},
             time_limit=PDF_GENERATION_TIME_LIMIT)
def generate_pdf(document_id, document_type):
    document = BillingDocumentBase.objects.get(id=document_id, kind=document_type)
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
    