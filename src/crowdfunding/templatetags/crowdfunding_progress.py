import logging
import datetime
import pytz
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_DOWN
from django import template
from django.db.models import Sum
from community.helpers import get_community
from moderation.models import UserCategoryRelationship
from crowdfunding.project import (
    get_year_investor_count,
    get_year_public_investor_count,
    get_year_private_investor_count,
    get_project,
    get_project_year_start,
    get_project_year_end,
)
from moderation.social import update_social_ids
from crowdfunding.models import ProjectInvestment, Tier

logger = logging.getLogger(__name__)

register = template.Library()

@register.simple_tag(takes_context=True)
def project_start_date(context):
    project=get_project(context)
    year = context.get("year")
    start_date = get_project_year_start(project, year)
    return start_date

@register.simple_tag(takes_context=True)
def project_end_date(context):
    project=get_project(context)
    year = context.get("year")
    end_date = get_project_year_end(project, year)
    return end_date

@register.inclusion_tag('crowdfunding/progress.html', takes_context=True)
def progress_bar(context):
    project=get_project(context)
    year = context.get("year")
    start_date = get_project_year_start(project, year)
    end_date = get_project_year_end(project, year)
    dct = {}
    total_dec = ProjectInvestment.objects \
                                .filter(
                                     paid=True,
                                     project=project,
                                     datetime__gte=start_date,
                                     datetime__lt=end_date,
                                ) \
                                .aggregate(total=Sum('pledged')) \
                                ['total']
    try:
        total_int = round(total_dec)
    except TypeError:
        total_int = 0
    
    dct["current"] = total_int
    
    try:
        goal = get_project(context).goal
    except AttributeError:
        goal = 0

    try:
        percentage = Decimal(total_int / goal * 100)
        percentage = percentage.quantize(Decimal('.01'), rounding=ROUND_DOWN)
    except ZeroDivisionError as err:
        logger.debug(err)  
        percentage = 0
        
    dct['percentage'] = percentage
    dct['goal'] = goal
    return dct

@register.simple_tag(takes_context=True)
def year_total_investor_count(context):
    return get_year_investor_count(context)

@register.simple_tag(takes_context=True)
def year_public_investor_count(context):
    return get_year_public_investor_count(context)

@register.simple_tag(takes_context=True)
def year_private_investor_count(context):
    return get_year_private_investor_count(context)

@register.simple_tag(takes_context=True)
def project_name(context):
    try:
        return get_project(context).name
    except AttributeError:
        return None
    
@register.simple_tag(takes_context=True)
def year_range(context):
    project = get_project(context)
    if not project:
        return []
    # year range
    start_dt = project.start_date
    difference_in_years = relativedelta(
        datetime.datetime.now(pytz.utc),
        start_dt
    ).years
    year_range = reversed(range(difference_in_years+1))
    return year_range
    


def get_active_member_count(members_userid_lst, followers_userid_lst):
    if not members_userid_lst or not followers_userid_lst:
        return 0
    return len(set(members_userid_lst) & set(followers_userid_lst))

@register.inclusion_tag('crowdfunding/investor_list.html', takes_context=True)
def investor_list(context):
    project=get_project(context)
    year = context.get("year")
    start_date = get_project_year_start(project, year)
    end_date = get_project_year_end(project, year)
    tier_lst = []
    funder_lst = []
    if Tier.objects.filter(project=project).count():
        for t in Tier.objects.filter(project=project):
            tier = {}
            tier['title']= t.title
            tier['emoji']= t.emoji
            tier['description']= t.description
            tier['funder_lst'] = list(ProjectInvestment.objects.
                                      filter(paid=True).
                                      filter(public=True).
                                      filter(project=project).
                                      filter(datetime__gte=start_date).
                                      filter(datetime__lt=end_date).
                                      filter(pledged__gte=t.min, pledged__lte=t.max))
            tier_lst.append(tier)
    else:
        funder_lst = list(ProjectInvestment.objects.
                                      filter(paid=True).
                                      filter(public=True).
                                      filter(project=project).
                                      filter(datetime__gte=start_date).
                                      filter(datetime__lt=end_date).
                                      order_by('name').
                                      distinct('name'))
    return {
        'tiers': tier_lst,
        'funders': funder_lst,
    }

@register.inclusion_tag('crowdfunding/investor_progress_bar.html', takes_context=True)
def investor_progress_bar(context):
    """
    From the point of view of the current community:
    how many investors in our crowdfunding?
    how many active members (members following the bot) in our community?
    active members: intersection of bot followers and members
    members: users belonging to membership categories according to moderators we trust
    percentage of investors / active members?
    """
    project=get_project(context)
    if not project:
        return {
            "investor_count": 0,
            "active_member_count": 0,
            "percentage": 0,
        }
    year = context.get("year")
    community = get_community(context)
    logger.info(f"community: {community}")
    investor_count: int = get_year_investor_count(context)
    end_dt =get_project_year_end(project, year)
    members_userid_qs = UserCategoryRelationship.objects.filter(
        community__in=community.trust.all(),
        category__in=community.membership.all(),
        created__lt=end_dt,
        ).distinct('social_user').values_list('social_user__user_id', flat=True)
    members_userid_lst = list(members_userid_qs)
    logger.info(f"members_userid_lst: {members_userid_lst}")
    bot_userid = community.account.userid
    bot_screen_name = community.account.username
    logger.info(f"bot_screen_name {bot_screen_name}")
    logger.info(f"bot_userid {bot_userid}")
    followers_userid_lst = update_social_ids(
        bot_screen_name,
        cached=True,
        bot_screen_name=bot_screen_name,
        relationship='followers',
        )
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
        "active_member_count": active_member_count,
        "percentage": percentage
    }