from decimal import Decimal, ROUND_DOWN
from django import template
from django.db.models import Sum
from django.conf import settings
from ..models import ProjectInvestment, Project

register = template.Library()

@register.inclusion_tag('crowdfunding/progress.html')
def progress_bar():
    context_dict = {}
    current_dict = ProjectInvestment.objects.aggregate(current=Sum('pledged'))
    context_dict.update(current_dict)
    goal = Project.objects.get(name=settings.PROJECT_NAME).goal
    try:
        percentage = current_dict['current']/goal*100
    except:
        percentage = 0
        
    percentage = percentage.quantize(Decimal('.01'), rounding=ROUND_DOWN)
    context_dict['percentage'] = percentage
    context_dict['goal'] = goal
    return context_dict