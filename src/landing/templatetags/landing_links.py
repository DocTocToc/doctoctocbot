import logging

from django import template
from django.utils.safestring import mark_safe
from django.contrib.sites.shortcuts import get_current_site
from mastodon.helpers import webfinger_url
from community.helpers import get_community

logger = logging.getLogger(__name__)

register = template.Library()

@register.simple_tag(takes_context=True)
def twitter_bot_username(context):
    community = get_community(context['request'])
    try:
        return community.account.username
    except AttributeError:
        return

@register.simple_tag(takes_context=True)
def mastodon_bot_username(context):
    community = get_community(context['request'])
    try:
        return f'@{community.mastodon_account.acct}'
    except AttributeError:
        return

@register.simple_tag(takes_context=True)
def mastodon_bot_url(context):
    community = get_community(context['request'])
    try:
        return webfinger_url(community.mastodon_account.acct)
    except AttributeError:
        return

@register.simple_tag(takes_context=True) 
def twitter_bot_username_arobase(context):
    return f"@{twitter_bot_username(context)}"
    
@register.simple_tag(takes_context=True)
def bot_link_text(context):
    screen_name = twitter_bot_username(context)
    return mark_safe(f'<a href="https://twitter.com/{screen_name}">🤖@{screen_name}</a>')
    
@register.simple_tag(takes_context=True)
def bot_link_emoji(context):
    screen_name = twitter_bot_username(context)
    return mark_safe(f'<a href="https://twitter.com/{screen_name}">🤖</a>')
    
@register.simple_tag(takes_context=True)
def twitter_bot_url(context):
    screen_name = twitter_bot_username(context)
    return mark_safe(f'https://twitter.com/{screen_name}')

@register.simple_tag(takes_context=True)
def site_link_text(context):
    site = get_current_site(context)
    return mark_safe(f'<a href="/">{site.name}</a>')
