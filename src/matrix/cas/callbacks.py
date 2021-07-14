import logging
logger = logging.getLogger(__name__)
from constance import config
from matrix.models import CategoryAccessControl, FilterSocial
from moderation.models import Friend, Follower

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
    if filtersocial(user):
        return True

def _filter(fs, socialuser):
    def _filter_friend(fs, socialuser):
        friend_ids = Friend.objects.filter(user=socialuser).latest().id_list
        friend_filter_ids = []
        for category in fs.friend_category.all():
            friend_filter_ids.extend(category.socialuser_set.values_list("user_id", flat=True))
        return len(set(friend_ids) & set(friend_filter_ids)) >= fs.friend_lower
            
    def _filter_follower(fs, socialuser):
        if not Follower.objects.filter(user=socialuser).exists():
            logger.debug(f"No Follower object for {socialuser}")
            return
        follower_ids = Follower.objects.filter(user=socialuser).latest().id_list
        logger.debug(f"{follower_ids=}")
        follower_filter_ids = []
        for category in fs.follower_category.all():
            follower_filter_ids.extend(category.socialuser_set.values_list("user_id", flat=True))
        return len(set(follower_ids) & set(follower_filter_ids)) >= fs.follower_lower

    has_friend_filter = fs.friend_category.all() and fs.friend_lower
    has_follower_filter = fs.follower_category.all() and fs.follower_lower
    
    # empty filter
    if not has_friend_filter and not has_follower_filter:
        return False

    friend_filter = None
    if has_friend_filter:
        friend_filter = _filter_friend(fs, socialuser)
    
    follower_filter = None
    if has_follower_filter:
        follower_filter = _filter_follower(fs, socialuser)

    # if both kinds are present, both must be True
    if has_friend_filter and has_follower_filter:
        return friend_filter and follower_filter
    elif has_friend_filter and friend_filter:
        return True
    elif has_follower_filter and follower_filter:
        return True
    return False

def filtersocial(user):
    """Goes through the social filters and if one passes, return True.
    Else, return False
    """
    socialuser = user.socialuser
    if not socialuser:
        return False
    for fs in FilterSocial.objects.filter(active=True):
        if _filter(fs, socialuser):
            return True
    return False