import logging
import datetime

from django import template
from django.utils.safestring import mark_safe
from django.utils.formats import date_format
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import DatabaseError
from community.models import Community
from django.conf import settings


from community.helpers import get_community, activate_language
from community.models import Retweet

logger = logging.getLogger(__name__)

register = template.Library()


@register.simple_tag(takes_context=True)
def site_text(context):
    site = get_current_site(context)
    return site.name

@register.simple_tag(takes_context=True)
def community_name(context):
    site = get_current_site(context)
    try:
        return site.community.name
    except Community.DoesNotExist:
        logger.error(f"Site {site} has no community.")
        return

def get_hashtag_lst(context):
    community = get_community(context['request'])
    try:
        return list(
            Retweet.objects.filter(
                community=community,
                retweet=True).values_list('hashtag__hashtag', flat=True).distinct().order_by()
        )
    except DatabaseError:
        return

@register.inclusion_tag('landing/hashtag_lst_and.html', takes_context=True)
def hashtag_lst_and(context):
    hashtag_lst = get_hashtag_lst(context)
    return {'hashtag_lst': hashtag_lst}

@register.inclusion_tag('landing/hashtag_lst_or.html', takes_context=True)
def hashtag_lst_or(context):
    hashtag_lst = get_hashtag_lst(context)
    return {'hashtag_lst': hashtag_lst}

@register.simple_tag(takes_context=True)
def hashtag(context):
    hashtag_lst = get_hashtag_lst(context)
    if hashtag_lst:
        return hashtag_lst[0]

@register.inclusion_tag('landing/category_and_lst.html', takes_context=True)
def membership_category_and(context):
    return {'category_lst': membership_category_label_lst(context)}

@register.inclusion_tag('landing/category_or_lst.html', takes_context=True)
def membership_category_or(context):
    return {'category_lst': membership_category_label_lst(context)}


def retweeted_category_values_list(context):
    community = get_community(context['request'])
    activate_language(community)
    rt_qs = Retweet.objects.filter(
        community=community,
        retweet=True
    )
    lst = [rt.category.label for rt in rt_qs]
    return lst
    
@register.inclusion_tag('landing/category_or_lst.html', takes_context=True)
def retweeted_category_or(context):
    return {
        'category_lst': retweeted_category_values_list(context)
    }

@register.inclusion_tag('landing/category_and_lst.html', takes_context=True)
def retweeted_category_and(context):
    try:
        return {
            'category_lst': retweeted_category_values_list(context)
        }
    except DatabaseError:
        return
    
@register.inclusion_tag('landing/category_ul.html', takes_context=True)
def retweeted_category_ul(context):
    try:
        return {
            'category_lst': retweeted_category_values_list(context)
        }
    except DatabaseError:
        return
    
@register.inclusion_tag('landing/category_ul.html', takes_context=True)
def follower_category_ul(context):
    try:
        return {
            'category_lst': follower_category_label_lst(context)
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
    for field in field_lst:
        if not field:
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
    community = get_community(context['request'])
    if not community:
        return
    try:
        lang = context["LANGUAGE_CODE"][:2]
        logger.debug(f"lang: '{lang}'")
    except:
        lang = "en"
    field = f"field__{lang}"
    return list(
            community.membership.values_list(field, flat=True)
    )

def follower_category_field_lst(context):
    """
    TODO: return in the language adapted to context or community
    This function will return None if Mesh model is empty.
    Please apply mesh app fixture mesh_fr_en.json first.
    """
    community = get_community(context['request'])
    try:
        lang = context["LANGUAGE_CODE"][:2]
        logger.debug(f"lang: '{lang}'")
    except:
        lang = "en"
    field = f"field__{lang}"
    return list(
            community.follower.values_list(field, flat=True)
    )
    
def membership_category_label_lst(context):
    """
    Return list of strings representing the different category of a community's members
    """
    community = get_community(context['request'])
    return list(community.membership.values_list("label", flat=True))

def follower_category_label_lst(context):
    """
    Return list of strings representing the different category of a community's allowed followers
    """
    community = get_community(context['request'])
    return list(community.follower.values_list("label", flat=True))

    
def retweeted_category_field_lst(context):
    """
    TODO: return in the language adapted to context or community
    """
    community = get_community(context['request'])
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
    community = get_community(context['request'])
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
    community = get_community(context['request'])
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

@register.inclusion_tag('landing/network_navbar.html', takes_context=True)    
def network_navbar(context):
    community = get_community(context['request'])
    if not community:
        logger.warn("Create a community first.")
        return
    network_lst = Community.objects \
        .exclude(id=community.id) \
        .exclude(active=False) \
        .values('name', 'site__domain')
    logger.debug(network_lst)
    if settings.DEBUG:
        protocol="http://"
    else:
        protocol="https://"
    for node in network_lst:
        logger.debug(node)
        url = mark_safe(f"{protocol}{node['site__domain']}")
        node['site__domain']= url
        logger.debug(node)
    logger.debug(network_lst)
    return {'network': network_lst}