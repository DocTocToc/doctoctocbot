import logging
from community.helpers import activate_language, get_community
from django import template
from django.db.utils import DatabaseError

from matrix.models import CategoryAccessControl

logger = logging.getLogger(__name__)

register = template.Library()

@register.inclusion_tag('matrix/category_ul.html', takes_context=True)
def matrix_category_lst(context):
    community = get_community(context.request)
    activate_language(community)
    try:
        category_lst= list(
            CategoryAccessControl.objects.filter(
                authorize=True,
            ).values_list('category__label', flat=True).distinct().order_by()
        )
    except DatabaseError:
        category_lst=None
    return {'category_lst': category_lst}
