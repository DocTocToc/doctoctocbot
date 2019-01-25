from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Project, ProjectInvestor

@receiver(post_save, sender=ProjectInvestor)
def update_amount_paid(sender, instance, created, **kwargs):
    project_mi = instance.project
    project_mi.amount_paid = sum(ProjectInvestor.objects.filter(paid=True).values_list('pledged', flat=True))
    project_mi.save()

@receiver(post_save, sender=ProjectInvestor)
def update_investor_count(sender, instance, created, **kwargs):
    project_mi = instance.project
    project_mi.investor_count = ProjectInvestor.objects.filter(paid=True).distinct('user').count()
    project_mi.save()

@receiver(post_save, sender=ProjectInvestor)
def update_transaction_count(sender, instance, created, **kwargs):
    project_mi = instance.project
    project_mi.transaction_count = ProjectInvestor.objects.filter(paid=True).count()
    project_mi.save()