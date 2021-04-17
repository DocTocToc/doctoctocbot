import logging
logger = logging.getLogger(__name__)
from constance import config
from matrix.models import CategoryAccessControl

def matrix_attributes(user, service):
    """Return a dict with values required by a Matrix server CAS SSO."""
    required_attribute_key = config.matrix__cas__callbacks__attribute_key
    required_attribute_value = config.matrix__cas__callbacks__attribute_value
    attributes = {}
    attributes['username'] = user.get_username()
    attributes['name'] = user.get_username()
    if authorize(user):
        attributes[required_attribute_key] = required_attribute_value
    #attributes['full_name'] = user.get_full_name()
    #attributes['short_name'] = user.get_short_name()
    return attributes

def authorize(user):
    """Return True if a given user is authorized to login to Matrix server"""
    if not user:
        return False
    if not user.socialuser:
        logger.error(f"No socialuser for {user}")
        return False
    user_category_qs = user.socialuser.category.all()
    if not user_category_qs:
        return False
    # NO access set of categories
    # (unauthorized categories should NOT have access)
    no_category_set = set(
        CategoryAccessControl.objects\
        .filter(authorize=False).values_list("category", flat=True)
    )
    user_category_set = set(
        user.socialuser.category.values_list("id", flat=True)
    )
    # if the intersection of user cat set and blocked cat set is not empty:
    # NO access
    if user_category_set & no_category_set:
        return False
    # YES access set of categories
    # (authorized categories should have access)
    yes_category_set = set(
        CategoryAccessControl.objects\
        .filter(authorize=True).values_list("category", flat=True)
    )
    # if one or more categories of the user belonged to authorized categories:
    # YES access (grant access)
    if user_category_set & yes_category_set:
        return True