"""
<meta name="twitter:card" content="summary" />
<meta name="twitter:site" content="{{twitter_site}}" />
<meta name="twitter:creator" content="{{twitter_creator}}" />
<meta property="og:url" content="{{og_url}}" />
<meta property="og:title" content="{{og_title}}" />
<meta property="og:description" content="{{og_description}}" />
<meta property="og:image" content="{{og_image}}" />
"""
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
from django.utils.translation import gettext as _
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from community.helpers import get_community, activate_language
from community.models import Retweet

from constance import config

logger = logging.getLogger(__name__)

register = template.Library()

# output = _('Today is %(month)s %(day)s.') % {'month': m, 'day': d}

@register.inclusion_tag('landing/twitter_opengraph.html', takes_context=True)
def opengraph(context):
    community = get_community(context['request'])

    activate_language(community)
    try:
        twitter_site = f"@{community.account.username}"
    except AttributeError:
        twitter_site = ""
    twitter_creator = (
        context.get("twitter_creator")
        or config.landing__templatetags__opengraph_tags__twitter_creator
    )
    try:
        site_name = community.site.name
    except AttributeError:
        site_name = ""
    og_title = (
        context.get("og_title")
        or site_name
    )
    og_description = (
        context.get("og_description")
        or _('Welcome to %(twitter_site)s companion website.' % {'twitter_site': twitter_site})
    )
    request = context['request']
    og_url = (
        context.get("og_url")
        or request.build_absolute_uri()
    )
    og_image = (
        context.get("og_image")
        or request.build_absolute_uri(staticfiles_storage.url('doctocnet/bot_logo_400x400.jpg'))
    )
    return {
        'twitter_site': twitter_site,
        'twitter_creator': twitter_creator,
        'og_url': og_url,
        'og_title': og_title,
        'og_description': og_description,
        'og_image': og_image,
    }