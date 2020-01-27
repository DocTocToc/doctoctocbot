import logging
from discourse.models import AccessControl
from moderation.social import get_socialuser_from_screen_name
from discourse.api import add_username_to_group

logger = logging.getLogger(__name__)

def user_created_pipe(userid, username):
    add_group(username)

def add_group(username):
    """ Add user to a Discussion group according to its category"""
    su = get_socialuser_from_screen_name(username)
    if not su:
        return
    for category in su.category.all():
        group = category.accesscontrol.group
        add_username_to_group(
            username=username,
            groupname=group
        )    