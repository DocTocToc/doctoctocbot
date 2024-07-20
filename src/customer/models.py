import uuid
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator
from django.utils.translation import gettext_lazy as _

from common.international import countries, currencies

def default_language():
    return settings.LANGUAGE_CODE


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    silver_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
        help_text=_("Id of corresponding Silver Customer record.")
    )
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Django user"),
        verbose_name=_("User")
    )
    first_name = models.CharField(
        max_length=255,
        help_text=_("First name"),
        verbose_name=_("First name"),
    )
    last_name = models.CharField(
        max_length=255,
        help_text=_("Last name"),
        verbose_name=_("Last name"),
    )
    company = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Company"),
        verbose_name=_("Company"),
    )
    email = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Email"),
        verbose_name=_("Email"),
    )
    address_1 = models.CharField(
        max_length=255,
        help_text=_("Address Line 1"),
        verbose_name=_("Address Line 1"),
    )
    address_2 = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Address Line 2 (optional)"),
        verbose_name=_("Address Line 2 (optional)"), 
    )
    country = models.CharField(
        choices=countries,
        max_length=3,
        help_text=_("Country"),
        verbose_name=_("Country"),
    )
    city = models.CharField(
        max_length=255,
        help_text=_("City"),
        verbose_name=_("City"),
    )
    state = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("State"),
        verbose_name=_("State"),
    )
    zip_code = models.PositiveIntegerField(
        null = True,
        help_text=_("ZIP code"),
        verbose_name=_("ZIP code"),
    )
    language = models.CharField(
        max_length=35,
        help_text=_("Language"),
        verbose_name=_("Language"),
        default=default_language,
    )

    class Meta:
        app_label = 'customer'

    def __str__(self):
        return "{}:{}".format(self.id, self.user)
    
    @staticmethod
    def has_read_permission(self):
        return True

    def has_write_permission(self):
        return False
    
    def has_update_permission(self):
        return False
    
    def has_object_read_permission(self, request):
        #logger.debug(f"request.user.socialuser: {request.user.socialuser}")
        #logger.debug(f"self.socialuser: {self.socialuser}")
        try:
            return (
                self.user == request.user 
            )
        except:
            return False

    def has_object_write_permission(self, request):
        return False

    def has_object_update_permission(self, request):
        return False

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
    silver_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
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

    class Meta:
        app_label = 'customer'

    def __str__(self):
        return "{}:{}:{}".format(self.id, self.name, self.company)   


class Product(models.Model):
    silver_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    product_code = models.CharField(max_length=255, blank=True, null=True, unique=True)
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

    class Meta:
        app_label = 'customer'

    def __str__(self):
        return "{}:{}:{}".format(self.id, self.product_code, self.description)  