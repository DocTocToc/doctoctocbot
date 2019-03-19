import logging
from decimal import Decimal, ROUND_DOWN
from django import template
from django.db.models import Sum
from django.conf import settings
from ..models import ProjectInvestment, Project

logger = logging.getLogger(__name__)

register = template.Library()

@register.inclusion_tag('crowdfunding/progress.html')
def progress_bar():
    context_dict = {}
    
    total_dec = ProjectInvestment.objects \
                                 .filter(paid=True) \
                                 .aggregate(total=Sum('pledged')) \
                                 ['total']
    try:
        total_int = round(total_dec)
    except TypeError:
        total_int = 0
    
    context_dict["current"] = total_int
    
    goal = Project.objects.get(name=settings.PROJECT_NAME).goal
    try:
        percentage = Decimal(total_int / goal * 100)
        percentage = percentage.quantize(Decimal('.01'), rounding=ROUND_DOWN)
    except ZeroDivisionError as err:
        logger.debug(err)  
        percentage = 0
        
    context_dict['percentage'] = percentage
    context_dict['goal'] = goal
    return context_dict