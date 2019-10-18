from django import template
from moderation.models import Category

register = template.Library()

@register.filter(name='is_moderator')
def is_moderator(user):
    try:
        moderator_category=Category.objects.get(name="moderator")
    except:
        return False
    try:
        return moderator_category in user.socialuser.category.all()
    except:
        return False
