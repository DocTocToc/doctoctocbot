import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from common.international import currencies
from django.contrib.sites.models import Site


class ProjectManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Project(models.Model):
    name = models.CharField(
        max_length=191,
        unique=True,
    )
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
    
    objects = ProjectManager()

    def __str__(self):
        return "{}:{}".format(self.id, self.name)
    
    def natural_key(self):
        return (self.name,)


class ProjectInvestment(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE
    )
    campaign = models.ForeignKey(
        'Campaign',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
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
    payment_intent=models.CharField(max_length=27, blank=True)
    
    def __str__(self):
        return "{}:{} user:{} pledged:{} paid:{} payment_intent:{}".format(
            self.uuid,
            self.project,
            self.user,
            self.pledged,
            self.paid,
            self.payment_intent
        )

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

    def get_rank(self):
        current_campaign = Campaign.objects.filter(
            project=self.project,
            start_datetime__gte=self.datetime,
            end_datetime__lte=self.datetime
        ).first()
        qs = ProjectInvestment.objects \
            .filter(paid=True) \
            .filter(project=self.project) \
            .filter(datetime__lte=self.datetime)
        if current_campaign:
            qs.filter(datetime__gte=current_campaign.start_datetime)
        return qs.count()


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


class Campaign(models.Model):
    project = models.ForeignKey(
        'crowdfunding.Project',
        on_delete=models.CASCADE,
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    goal = models.IntegerField(blank=True)
    
    class Meta:
        ordering = ['start_datetime']
    
    def __str__(self):
        return "Campaign {}:{} ({} - {})".format(
            self.id,
            self.project.name,
            self.start_datetime.date(),
            self.end_datetime.date(),
        )


class PaymentProcessorWebhook(models.Model):
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
    )
    secret = models.CharField(
        max_length=255
    )
    
    def __str__(self):
        return "{}:{}:{}".format(
            self.id,
            self.site,
            "*" * len(self.secret),
        )