from django.contrib.auth import get_user_model
from django.db import models
import uuid

from common.international import countries


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    copper_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    address_1 = models.CharField(max_length=255, blank=True)
    address_2 = models.CharField(max_length=255, blank=True)
    country = models.CharField(choices=countries, max_length=3)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    zip_code = models.PositiveIntegerField(null = True, blank=True)


STATE_CHOICES = (
    (1, "issued")
    )

class Provider(models.Model):
    DRAFT = 'draft'
    ISSUED = 'issued'
    PAID = 'paid'
    CANCELED = 'canceled'
    PROFORMA_INVOICE_CHOICES = [
        (DRAFT, 'Draft'),
        (ISSUED, 'Issued'),
        (PAID, 'Paid'),
        (CANCELED, 'Canceled'),
    ]
    PROFORMA = 'proforma'
    INVOICE = 'invoice'
    FLOW_CHOICES = [
        (PROFORMA, 'Proforma'),
        (INVOICE, 'Invoice'),    
    ]
    copper_provider_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    name = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    address_1 = models.CharField(max_length=255, blank=True)
    address_2 = models.CharField(max_length=255, blank=True)
    country = models.CharField(choices=countries, max_length=3)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    zip_code = models.PositiveIntegerField(null = True, blank=True)
    extra = models.TextField(blank=True)
    flow = models.CharField(
        max_length=8,
        choices=FLOW_CHOICES,
        default=INVOICE,
    )
    invoice_series = models.CharField(max_length=255, blank=True)
    invoice_starting_number = models.PositiveIntegerField(default=1)
    proforma_series = models.CharField(max_length=255, blank=True)
    proforma_starting_number = models.PositiveIntegerField(default=1)
    default_document_state = models.CharField(
        max_length=8,
        choices=PROFORMA_INVOICE_CHOICES,
        default=DRAFT,
    )
    meta = models.CharField(max_length=255, blank=True)
    

