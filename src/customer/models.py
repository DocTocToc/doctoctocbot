import uuid
from decimal import *

from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator

from common.international import countries, currencies


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
    copper_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
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

class Product(models.Model):
    product_code = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    unit = models.CharField(max_length=255, blank=True)
    unit_price = models.DecimalField(
        default=Decimal('0.00'),
        max_digits=8,
        decimal_places=2,
    )
    sales_tax_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MaxValueValidator(100),
        ]
    )
    sales_tax_name = models.CharField(max_length=255, blank=True)
    currency = models.CharField(
        choices=currencies,
        max_length=4,
        default='EUR',
        help_text='The currency used for billing.'
    )