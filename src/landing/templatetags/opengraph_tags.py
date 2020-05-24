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
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.staticfiles.storage import staticfiles_storage
from community.helpers import get_community, activate_language
from community.models import Retweet

logger = logging.getLogger(__name__)

register = template.Library()

# output = _('Today is %(month)s %(day)s.') % {'month': m, 'day': d}

@register.inclusion_tag('landing/twitter_opengraph.html', takes_context=True)
def opengraph(context):
    community = get_community(context)
    activate_language(community)
    twitter_site = f"@{community.account.username}"
    twitter_creator = "@MedecineLibre"
    og_url = f"https://{community.site.domain}"
    og_title = community.site.name
    og_description = _('Welcome to %(twitter_site)s companion website.' % {'twitter_site': twitter_site})
    request = context['request']
    og_image = request.build_absolute_uri(staticfiles_storage.url('doctocnet/bot_logo_400x400.jpg'))
    return {
        'twitter_site': twitter_site,
        'twitter_creator': twitter_creator,
        'og_url': og_url,
        'og_title': og_title,
        'og_description': og_description,
        'og_image': og_image,
    }