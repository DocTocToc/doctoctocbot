import logging

from django import template
from django.utils.safestring import mark_safe
from django.contrib.sites.shortcuts import get_current_site

from landing.templatetags.helpers import get_community

logger = logging.getLogger(__name__)

register = template.Library()

@register.simple_tag(takes_context=True)
def bot_screen_name(context):
    community = get_community(context)
    try:
        return community.account.username
    except AttributeError:
        return

@register.simple_tag(takes_context=True)
def bot_link_text(context):
    screen_name = bot_screen_name(context)
    return mark_safe(f'<a href="https://twitter.com/{screen_name}">🤖@{screen_name}</a>')
    
@register.simple_tag(takes_context=True)
def bot_link_emoji(context):
    screen_name = bot_screen_name(context)
    return mark_safe(f'<a href="https://twitter.com/{screen_name}">🤖</a>')
    
@register.simple_tag(takes_context=True)
def bot_url(context):
    screen_name = bot_screen_name(context)
    return mark_safe(f'https://twitter.com/{screen_name}')

@register.simple_tag(takes_context=True)
def site_link_text(context):
    site = get_current_site(context)
    return mark_safe(f'<a href="/">{site.name}</a>')
