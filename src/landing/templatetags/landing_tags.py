import logging
import datetime

from django import template
from django.utils.safestring import mark_safe
from django.utils.formats import date_format
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import DatabaseError


from community.helpers import get_community
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
    try:
        return {
            'hashtag_lst': list(
                Retweet.objects.filter(
                    community=community,
                    retweet=True).values_list('hashtag__hashtag', flat=True).distinct().order_by()
            )
        }
    except DatabaseError:
        return

@register.inclusion_tag('landing/category_and_lst.html', takes_context=True)
def membership_category_and(context):
    return {'category_lst': membership_category_label_lst(context)}

@register.inclusion_tag('landing/category_or_lst.html', takes_context=True)
def membership_category_or(context):
    return {'category_lst': membership_category_label_lst(context)}
    
@register.inclusion_tag('landing/category_or_lst.html', takes_context=True)
def retweeted_category_or(context):
    community = get_community(context)
    return {
        'category_lst': list(
            Retweet.objects.filter(
                community=community,
                retweet=True).values_list('category__label', flat=True).distinct().order_by()
        )
    }

@register.inclusion_tag('landing/category_and_lst.html', takes_context=True)
def retweeted_category_and(context):
    community = get_community(context)
    try:
        return {
            'category_lst': list(
                Retweet.objects.filter(
                    community=community,
                    retweet=True).values_list('category__label', flat=True).distinct().order_by()
            )
        }
    except DatabaseError:
        return
    
@register.inclusion_tag('landing/category_lst.html', takes_context=True)
def membership_field_lst_formatted(context):
    return {'category_lst': membership_category_field_lst(context)}

@register.simple_tag(takes_context=True)
def membership_field_lst_plain(context):
    field_lst = membership_category_field_lst(context)
    logger.debug(field_lst)
    if not field_lst:
        return
    if isinstance(field_lst, list) and len(field_lst)>1:
        return ", ".join(field_lst)
    elif isinstance(field_lst, list) and len(field_lst)>0:
        return field_lst[0]

def membership_category_field_lst(context):
    """
    TODO: return in the language adapted to context or community
    This function will return None if Mesh model is empty.
    Please apply mesh app fixture mesh_fr_en.json first.
    """
    community = get_community(context)
    try:
        lang = context["LANGUAGE_CODE"][:2]
        logger.debug(f"lang: '{lang}'")
    except:
        lang = "en"
    field = f"field__{lang}"
    return list(
            community.membership.values_list(field, flat=True)
    )
    
def membership_category_label_lst(context):
    """
    Return list of strings representing the different category of a community's members
    """
    community = get_community(context)
    return list(community.membership.values_list("label", flat=True))
    
def retweeted_category_field_lst(context):
    """
    TODO: return in the language adapted to context or community
    """
    community = get_community(context)
    try:
        lang = context["LANGUAGE_CODE"][:2]
        logger.debug(f"lang: '{lang}'")
    except:
        lang = "en"
    field = f"field__{lang}"
    return list(
            community.membership.values_list(field, flat=True)
    )

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
        return
    return date_format(datetime.date(), format_string)

@register.simple_tag(takes_context=True)
def bot_launch_date(context, format_string):
    """
    Return launch date of the bot
    """
    community = get_community(context)
    if not community:
        logger.warn("Create a community first.")
        return
    try:
        launch_date = community.account.launch
    except ObjectDoesNotExist as e:
        logger.warn(e)
    
    if launch_date:
        return date_format(launch_date, format_string)
    else:
        return community_creation_date(context, format_string)