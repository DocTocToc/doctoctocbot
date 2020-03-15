import logging
from typing import List
from django import template
from moderation.models import Category, Moderator, UserCategoryRelationship
from discourse.models import AccessControl
from django.db.utils import DatabaseError

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter(name='is_allowed_discussion')
def is_allowed_discussion(user):
    try:
        user_categories = user.socialuser.category.all()
    except:
        return False
    if not user_categories:
        return False
    # If user is a moderator, allow her (this prevents disallowing moderators
    # because their UserCategoryRelationship instances could appear as self
    # moderated)
    if Moderator.objects.filter(socialuser=user.socialuser).exists():
        return True
    # If user is dev, allow her
    try:
        dev: Category = Category.objects.get(name='dev')
    except Category.DoesNotExist:
        dev = None
    if dev in user_categories:
        return True
    try:
        allowed_category_id = (
            AccessControl.objects
            .filter(authorize=True)
            .values_list("category", flat=True)
        )
    except DatabaseError as e:
        logger.error("Error on database table AccessControl.", e)
        allowed_category_id = None
    if not allowed_category_id:
        return False
    # list of id of user categories except self-moderated
    user_categories_other = (
        UserCategoryRelationship.objects.filter(
            social_user=user.socialuser
        ).exclude(
            moderator=user.socialuser
        ).values_list('category', flat=True)
    )
    if not user_categories_other:
        return False
    # list of id of allowed categories
    allowed_category = Category.objects.filter(
        id__in=allowed_category_id
        ).values_list('id', flat=True)
    _is_allowed = bool(
        list(set(allowed_category).intersection(set(user_categories_other)))
    )
    logger.debug(f"_is_allowed: {_is_allowed}")
    return _is_allowed