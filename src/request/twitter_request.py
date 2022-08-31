import logging
from django.urls import reverse
from django.template import Template, Context

from bot.tweepy_api import get_api as tweepy_api
from bot.python_twitter_api import get_api as twitter_api
from community.helpers import site_url
from tweepy.error import TweepError

logger = logging.getLogger(__name__)

def get_incoming_friendship(community):
    try:
        screen_name=community.account.username
    except:
        return
    api = twitter_api(username=screen_name)
    try:
        return api.IncomingFriendship()
    except AttributeError:
        return
    except TweepError as e:
        logger.error(f'{e}')
    except Exception as e:
        logger.error(f'{e}')