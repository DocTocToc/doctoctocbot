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
    project = get_project(context)
    investor_count: int = get_total_investor_count(context)
    members_userid_lst = UserCategoryRelationship.objects.filter(
        community__in=community.trust.all(),
        category__in=community.membership.all()
        ).distinct('social_user').values_list('social_user__user_id', flat=True)
    bot_userid = community.account.userid
    followers_userid_lst = update_followersids(bot_userid)
    active_member_count = len(set(members_userid_lst) & set(followers_userid_lst))
    try:
        percentage = Decimal(investor_count / active_member_count * 100)
        percentage = percentage.quantize(Decimal('.01'), rounding=ROUND_DOWN)
    except ZeroDivisionError as err:
        logger.debug(err)  
        percentage = 0
    return {
        "investor_count": investor_count,
        "active_member_count": active_member_count,
        "percentage": percentage
    }