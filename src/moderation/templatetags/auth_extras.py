import logging
from django import template
from moderation.models import Category

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter(name='is_moderator')
def is_moderator(user):
    try:
        moderator_category=Category.objects.get(name="moderator")
    except:
        return False
    try:
        _is_moderator = moderator_category in user.socialuser.category.all()
        logger.debug(f"_is_moderator: {_is_moderator}")
        return _is_moderator
    except:
        return False