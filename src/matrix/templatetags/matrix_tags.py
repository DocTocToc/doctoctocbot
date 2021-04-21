import logging

from django import template
from django.db.utils import DatabaseError

from matrix.models import CategoryAccessControl

logger = logging.getLogger(__name__)

register = template.Library()

@register.inclusion_tag('matrix/category_ul.html')
def matrix_category_lst():
    try:
        category_lst= list(
            CategoryAccessControl.objects.filter(
                authorize=True,
            ).values_list('category__name', flat=True).distinct().order_by()
        )
    except DatabaseError:
        category_lst=None
    return {'category_lst': category_lst}
