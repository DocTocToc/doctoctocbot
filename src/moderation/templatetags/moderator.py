from django import template
from community.helpers import get_community
from moderation.models import Moderator

register = template.Library()

 
@register.simple_tag(takes_context=True)
def moderator_count(context):
    community = get_community(context['request'])
    count = Moderator.objects.filter(
        public = True,
        community = community
    ).count()
    return count