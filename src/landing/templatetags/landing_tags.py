import logging
import datetime

from django import template
from django.utils.safestring import mark_safe
from django.utils.formats import date_format
from django.contrib.sites.shortcuts import get_current_site

from landing.templatetags.helpers import get_community
from community.models import Retweet

logger = logging.getLogger(__name__)

register = template.Library()


@register.simple_tag(takes_context=True)
def site_text(context):
    site = get_current_site(context)
    return site.name

@register.inclusion_tag('landing/hashtag_lst.html', takes_context=True)
def hashtag_lst(context):
    community = get_community(context)
    return {
        'hashtag_lst': list(
            Retweet.objects.filter(
                community=community,
                retweet=True).values_list('hashtag__hashtag', flat=True).distinct().order_by()
        )
    }

@register.inclusion_tag('landing/category_lst.html', takes_context=True)
def category_lst(context):
    community = get_community(context)
    return {
        'category_lst': list(
            Retweet.objects.filter(
                community=community,
                retweet=True).values_list('category__label', flat=True).distinct().order_by()
        )
    }

@register.simple_tag(takes_context=True)
def community_creation_date(context, format_string):
    """
    Return creation date of the community as an ISO date time string
    """
    community = get_community(context)
    try:
        logger.debug(f"{community} \n {community.created}")
        datetime = community.created
    except:
        pass
    return date_format(datetime.date(), format_string)

@register.simple_tag(takes_context=True)
def bot_launch_date(context, format_string):
    """
    Return launch date of the bot
    """
    community = get_community(context)
    launch_date = community.account.launch
    if launch_date:
        return date_format(launch_date, format_string)
    else:
        return community_creation_date(context, format_string)