from django.db.models.signals import post_save
from django.dispatch import receiver
#from django.shortcuts import get_object_or_404

#from paypal.standard.ipn.signals import valid_ipn_received

from .models import ProjectInvestment

"""
@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn = sender
    if ipn.payment_status == 'Completed':
        # payment was successful
        order = get_object_or_404(ProjectInvestment, id=ipn.custom)
 
        if order.pledged == ipn.mc_gross:
            # mark the order as paid
            order.paid = True
            order.save()
"""

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
    
