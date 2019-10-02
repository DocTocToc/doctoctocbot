import logging
from decimal import Decimal, ROUND_DOWN
from django import template
from django.db.models import Sum
from django.conf import settings
from ..models import ProjectInvestment, Project
from crowdfunding.project import (
    get_total_investor_count,
    get_public_investor_count,
    get_private_investor_count,
    get_project
)

    

logger = logging.getLogger(__name__)

register = template.Library()

@register.inclusion_tag('crowdfunding/progress.html', takes_context=True)
def progress_bar(context):
    context_dict = {}
    
    total_dec = ProjectInvestment.objects \
                                .filter(
                                     paid=True,
                                     project=get_project(context)
                                ) \
                                .aggregate(total=Sum('pledged')) \
                                ['total']
    try:
        total_int = round(total_dec)
    except TypeError:
        total_int = 0
    
    context_dict["current"] = total_int
    
    try:
        goal = get_project(context).goal
    except AttributeError:
        goal = 0

    try:
        percentage = Decimal(total_int / goal * 100)
        percentage = percentage.quantize(Decimal('.01'), rounding=ROUND_DOWN)
    except ZeroDivisionError as err:
        logger.debug(err)  
        percentage = 0
        
    context_dict['percentage'] = percentage
    context_dict['goal'] = goal
    return context_dict

@register.simple_tag(takes_context=True)
def total_investor_count(context):
    return get_total_investor_count(context)

@register.simple_tag(takes_context=True)
def public_investor_count(context):
    return get_public_investor_count(context)

@register.simple_tag(takes_context=True)
def private_investor_count(context):
    return get_private_investor_count(context)

@register.simple_tag(takes_context=True)
def project_name(context):
    try:
        return get_project(context).name
    except AttributeError:
        return None
    