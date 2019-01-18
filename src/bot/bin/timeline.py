from typing import List

from ..twitter import get_api
from django.middleware.csrf import get_token

from timeline.models import add_status_tl, Status

def get_timeline():
    API = get_api()
    return API.user_timeline()

def get_timeline_id_lst(n=None) -> List:
    """
    Return n last tweet from timeline as a list of statusid, excluding replies
    """
    return [status.statusid
            for status
            in Status.objects.all().filter(json__contains={'in_reply_to_status_id': None})][:n]

def record_timeline():
    for status in get_timeline():
        add_status_tl(status)