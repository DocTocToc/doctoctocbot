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
from django.utils.translation import pgettext
from community.helpers import get_community
from community.models import Retweet

logger = logging.getLogger(__name__)

register = template.Library()


@register.simple_tag(takes_context=True)
def category(context):
    unknown = pgettext("category", "Unknown")
    try:
        category_lst = (
            context.request.user.socialuser.category.filter(public=True)
        )
    except:
        return [unknown]
    if not category_lst:
        return [unknown]
    label_lst = list()
    for category in category_lst:
        label_lst.append(category.label)
    return label_lst

@register.inclusion_tag('users/profile.html', takes_context=True)
def profile(context):
    def default_pp_url():
        return settings.MEDIA_URL + "twitter/profile/images/bigger/default_profile_bigger.png"
    if not context.request.user.is_authenticated:
        return
    su = context.request.user.socialuser
    if not su:
        name = context.request.user.get_full_name()
        screen_name = context.request.user.get_username()
        pp_url = default_pp_url()
    else:
        try:
            pp_url = su.profile.biggeravatar.url
        except:
            pp_url = default_pp_url()
        screen_name = su.screen_name_tag()
        name = su.name_tag()
    return {
        'profile': {
            'name' : name,
            'screen_name': screen_name,
            'pp_url': pp_url
        }
    }
    
@register.simple_tag(takes_context=True)
def screen_name(context):
    if not context.request.user.is_authenticated:
        return
    su = context.request.user.socialuser
    try:
        return su.screen_name_tag()
    except:
        return