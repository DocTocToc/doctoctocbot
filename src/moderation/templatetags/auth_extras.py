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

@register.filter(name='is_allowed_discussion')
def is_allowed_discussion(user):
    allowed_categories = []
    for category_name in ["physician",
                          "nurse",
                          "pharmacist",
                          "medical_student",
                          "midwife",
                          "physical_therapist"]:
        try:
            category = Category.objects.get(name=category_name)
            allowed_categories.append(category)
        except Category.DoesNotExist:
            continue
    try:
        user_categories = user.socialuser.category.all()
        logger.debug(f"user categories: {user_categories}")
        _is_allowed = bool(
            list(set(allowed_categories).intersection(set(user_categories)))
        )
        logger.debug(f"_is_allowed: {_is_allowed}")
        return _is_allowed
    except:
        return False