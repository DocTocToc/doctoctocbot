import logging
from django.urls import reverse
from django.template import Template, Context

from bot.tweepy_api import get_api
from community.helpers import site_url
from mytweepy.errors import HTTPException

logger = logging.getLogger(__name__)

def get_incoming_friendship(community):
    try:
        screen_name=community.account.username
    except:
        return
    api = get_api(username=screen_name, mt=True)
    try:
        return api.incoming_friendships()
    except AttributeError:
        return
    except HTTPException as e:
        logger.error(f'{e.api_errors=} {e.api_messages=}')
    except Exception as e:
        logger.error(f'{e}')