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
        category_lst = context.request.user.socialuser.category.all()
    except:
        return [unknown]
    if not category_lst:
        return [unknown]
    label_lst = list()
    for category in category_lst:
        label_lst.append(category.label)
    return label_lst