from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Project, ProjectInvestment

@receiver(post_save, sender=ProjectInvestment)
def update_amount_paid(sender, instance, created, **kwargs):
    project_mi = instance.project
    project_mi.amount_paid = sum(ProjectInvestment.objects.filter(paid=True).values_list('pledged', flat=True))
    project_mi.save()

@receiver(post_save, sender=ProjectInvestment)
def update_investor_count(sender, instance, created, **kwargs):
    project_mi = instance.project
    project_mi.investor_count = ProjectInvestment.objects.filter(paid=True).distinct('user').count()
    project_mi.save()

@receiver(post_save, sender=ProjectInvestment)
def update_transaction_count(sender, instance, created, **kwargs):
    project_mi = instance.project
    project_mi.transaction_count = ProjectInvestment.objects.filter(paid=True).count()
    project_mi.save()