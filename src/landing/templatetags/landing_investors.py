import logging
from decimal import Decimal, ROUND_DOWN
from django import template
from django.db.models import Sum
from django.conf import settings
from crowdfunding.models import ProjectInvestment, Project
from community.helpers import get_community
from crowdfunding.project import get_project
from crowdfunding.project import get_total_investor_count
from moderation.models import UserCategoryRelationship
from moderation.social import update_followersids

logger = logging.getLogger(__name__)

register = template.Library()

def get_active_member_count(members_userid_lst, followers_userid_lst):
    if not members_userid_lst or not followers_userid_lst:
        return 0
    return len(set(members_userid_lst) & set(followers_userid_lst))


@register.inclusion_tag('landing/investor_progress_bar.html', takes_context=True)
def investor_progress_bar(context):
    """
    From the point of view of the current community:
    how many investors in our crowdfunding?
    how many active members (members following the bot) in our community?
    active members: intersection of bot followers and members
    members: users belonging to membership categories according to moderators we trust
    percentage of investors / active members?
    """
    community = get_community(context)
    investor_count: int = get_total_investor_count(context)
    members_userid_qs = UserCategoryRelationship.objects.filter(
        community__in=community.trust.all(),
        category__in=community.membership.all()
        ).distinct('social_user').values_list('social_user__user_id', flat=True)
    members_userid_lst = list(members_userid_qs)
    logger.info(f"members_userid_lst: {members_userid_lst}")
    bot_userid = community.account.userid
    followers_userid_lst = update_followersids(bot_userid, cached=True)
    logger.info(f"followers_userid_lst {followers_userid_lst}")
    active_member_count = get_active_member_count(members_userid_lst, followers_userid_lst)
    try:
        percentage = Decimal(investor_count / active_member_count * 100)
        percentage = percentage.quantize(Decimal('.01'), rounding=ROUND_DOWN)
    except ZeroDivisionError as err:
        logger.debug(err)  
        percentage = 0
    return {
        "investor_count": investor_count,
        "active_member_count": _active_member_count,
        "percentage": percentage
    }