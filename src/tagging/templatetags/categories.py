import logging
import datetime

from django import template
from django.utils.safestring import mark_safe
from django.utils.formats import date_format
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import DatabaseError
from community.models import Community
from tagging.models import Category
from django.conf import settings


from community.helpers import get_community

logger = logging.getLogger(__name__)

register = template.Library()

@register.inclusion_tag('tagging/categories.html', takes_context=True)
def categories(context):
    community = get_community(context['request'])
    try:
        category_dct_lst= Category.objects.filter(
                    community=community,
                    hashtag=True).values('tag', 'summary', 'description')
    except DatabaseError:
        category_dct_lst=None
    logger.debug(f"category_dct_lst: {category_dct_lst}")
    return {'category_dct_lst': category_dct_lst}