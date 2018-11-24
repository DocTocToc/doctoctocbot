from django import template

register = template.Library()

@register.filter
def hashtag_count(value, arg):
    """Returns count for hashtag[arg]"""
    from conversation.utils import userhashtagcount
    return userhashtagcount(value, arg)

@register.filter
def total_hashtag_count(value):
    """Returns count for hashtag[arg]"""
    from conversation.utils import usertotalhashtagcount
    return usertotalhashtagcount(value)