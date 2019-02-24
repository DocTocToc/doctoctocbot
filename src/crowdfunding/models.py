import uuid

from django.conf import settings
from django.db import models


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

    def __str__(self):
        return "{}:{}".format(self.id, self.name)

class ProjectInvestment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    
    def __str__(self):
        return "{}:{} user:{} pledged:{} paid:{}".format(self.id, self.project, self.user, self.pledged, self.paid)