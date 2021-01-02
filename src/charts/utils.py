from moderation.models import UserCategoryRelationship
from community.helpers import get_community


def get_userid_lst(request):
    community = get_community(request)
    categories = community.membership.all()
    return UserCategoryRelationship.objects.filter(
        category__in = categories,
        community = community
        ).values_list('social_user__user_id', flat=True)