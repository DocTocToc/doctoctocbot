import logging
import datetime
import markdown
from django import template
from django.utils.safestring import mark_safe
from django.utils.formats import date_format
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import DatabaseError
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template import Template
from django.template.context import Context

from community.models import Community
from community.helpers import get_community, activate_language
from community.models import TextDescription, Text

logger = logging.getLogger(__name__)

register = template.Library()


@register.simple_tag(takes_context=True)
def guidelines(context):
    community = get_community(context)
    try:
        type = TextDescription.objects.get(name="guidelines")
    except TextDescription.DoesNotExist:
        return
    try:
        md = Text.objects.get(community=community, type=type).content
    except Text.DoesNotExist:
        return
    html = markdown.markdown(md)
    processed_html = Template(html).render(context=context)
    safe_html = mark_safe(processed_html)
    return safe_html
    