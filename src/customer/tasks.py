from silver.models import BillingDocumentBase
from celery import shared_task
from celery_once import QueueOnce
from django.conf import settings

PDF_GENERATION_TIME_LIMIT = getattr(settings, 'PDF_GENERATION_TIME_LIMIT',
                                    60)  # default 60s

@shared_task(base=QueueOnce, once={'graceful': True},
             time_limit=PDF_GENERATION_TIME_LIMIT)
def generate_pdf(document_id, document_type):
    document = BillingDocumentBase.objects.get(id=document_id, kind=document_type)
    document.generate_pdf()