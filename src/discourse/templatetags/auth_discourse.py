import logging
from typing import List
from django import template
from moderation.models import Category
from discourse.models import AccessControl
from django.db.utils import DatabaseError

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter(name='is_allowed_discussion')
def is_allowed_discussion(user):
    try:
        allowed_category_id: List = AccessControl.objects.filter(authorize=True).values_list("category", flat=True)
    except DatabaseError as e:
        logger.error("Error on database table AccessControl.", e)
        allowed_category_id = None
    if not allowed_category_id:
        return False
    allowed_category: List = Category.objects.filter(id__in=allowed_category_id)
    try:
        user_categories = user.socialuser.category.all()
        logger.debug(f"user categories: {user_categories}")
        _is_allowed = bool(
            list(set(allowed_category).intersection(set(user_categories)))
        )
        logger.debug(f"_is_allowed: {_is_allowed}")
        return _is_allowed
    except:
        return False