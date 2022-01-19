import logging
from django import template
from moderation.models import Moderator

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter(name='is_moderator')
def is_moderator(user):
    try:
        su = user.socialuser
    except AttributeError:
        #'AnonymousUser' object has no attribute 'socialuser'
        return False
    if not su:
        return False
    try:
        _is_moderator = Moderator.objects.filter(socialuser=su).exists()
        logger.debug(f"_is_moderator: {_is_moderator}")
        return _is_moderator
    except Moderator.DoesNotExist:
        return False