import logging
from moderation.models import UserCategoryRelationship
from community.helpers import get_community
from community.helpers import get_community_bot_socialuser
from users.utils import get_twitter_social_user

logger = logging.getLogger(__name__)

def get_bot_id(request):
    community = get_community(request)
    if not community:
        return
    bot_su = get_community_bot_socialuser(community)
    return bot_su.user_id

def get_user_id(request):
    logger.debug(f'{request.user=}')
    if not request.user.is_authenticated:
        return
    current_user = request.user
    logger.debug(f'{current_user=}')
    su = get_twitter_social_user(current_user)
    if not su:
        return
    return su.user_id

def get_userid_lst(request):
    community = get_community(request)
    categories = community.membership.all()
    return list(
        UserCategoryRelationship.objects.filter(
            category__in = categories
        ).values_list('social_user__user_id', flat=True)
    )