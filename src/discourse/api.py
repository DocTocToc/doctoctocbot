import logging
from pydiscourse import DiscourseClient
from pydiscourse.exceptions import DiscourseClientError
from django.conf import settings
logger=logging.getLogger(__name__)

def get_api_discourse():
    discourse_url = f"{settings.DISCOURSE_PROTOCOL}://{settings.DISCOURSE_HOSTNAME}"
    discourse_api = DiscourseClient(
        discourse_url,
        api_username='system',
        api_key=settings.DISCOURSE_API_KEY_SYSTEM)
    return discourse_api


def add_username_to_group(username, groupname):
    """Add a user to a group knowing with username and group name
    """
    groupid = group_id(groupname)
    api = get_api_discourse()
    try:
        response = api.add_group_member(groupid, username)
        logger.info(response)
    except DiscourseClientError as e:
        logger.error(e)
    
def group_id(groupname):
    """ Get group id from group name
    """
    api = get_api_discourse()
    for group in api.groups():
        if group["name"] == groupname:
            return group["id"]
    