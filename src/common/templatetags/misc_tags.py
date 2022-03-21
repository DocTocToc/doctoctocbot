from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from django.utils.text import normalize_newlines

register = template.Library()

@register.filter
def nowhitespace(value):
    return " ".join(value.split())

@register.filter
def cut_escape(value):
    return value.replace('\\n',' ').replace('\\"','"')