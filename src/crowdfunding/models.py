import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from common.international import currencies

class Project(models.Model):
    name = models.CharField(max_length=191)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    goal = models.IntegerField(blank=True)
    amount_paid = models.IntegerField(default=0)
    investor_count = models.IntegerField(default=0)
    transaction_count = models.IntegerField(default=0)
    investors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    provider = models.ForeignKey(
        'customer.Provider',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    product = models.ForeignKey(
        'customer.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    currency = models.CharField(
        choices=currencies, max_length=4, default='EUR',
        help_text='The currency used for billing.'
    )

    def __str__(self):
        return "{}:{}".format(self.id, self.name)

class ProjectInvestment(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True
    )
    name = models.CharField(max_length=191, blank=True)
    email = models.EmailField(blank=True)
    pledged = models.DecimalField(max_digits=6, decimal_places=2)
    paid = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)
    invoice = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=None,
        unique=True,
        help_text="Id of the invoice in the billing app."
    )
    invoice_pdf = models.BooleanField(default=False)
    
    def __str__(self):
        return "{}:{} user:{} pledged:{} paid:{}".format(self.uuid, self.project, self.user, self.pledged, self.paid)

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
                self.user == request.user and 
                self.paid == True 
            )
        except:
            return False

    def has_object_write_permission(self, request):
        return False

    def has_object_update_permission(self, request):
        return False


class Tier(models.Model):
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=50)
    slug = models.SlugField()
    description = models.CharField(max_length=191)
    emoji = models.CharField(max_length=4, blank=True)
    image = models.ImageField(blank=True)
    min = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0))
    max = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('Infinity'))


    class Meta:
        ordering = ['-max']
    

    def __str__(self):
        return "{}:{} / {} min: {} max: {}".format(self.id,
                                                   self.title,
                                                   self.description[:140],
                                                   self.min,
                                                   self.max)