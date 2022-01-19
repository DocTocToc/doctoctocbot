import logging
import markdown

from django import template
from django.utils.safestring import mark_safe
from django.template import Template


from community.helpers import get_community, activate_language
from community.models import TextDescription, Text


logger = logging.getLogger(__name__)

register = template.Library()

@register.simple_tag(takes_context=True)
def community_text(context, name):
    community = get_community(context['request'])
    try:
        text_type = TextDescription.objects.get(name=name)
    except TextDescription.DoesNotExist:
        return
    try:
        md = Text.objects.get(community=community, type=text_type).content
    except Text.DoesNotExist:
        return
    html = markdown.markdown(md)
    processed_html = Template(html).render(context=context)
    safe_html = mark_safe(processed_html)
    return safe_html
