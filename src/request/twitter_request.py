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

def message_requestor(queue):
    try:
        community = queue.community
    except:
        return
    try:
        helper_username = community.helper.username
    except:
        return
    if not helper_username:
        return
    try:
        requestor_screen_name = queue.socialuser.screen_name_tag()
    except:
        return
    if not requestor_screen_name:
        return
    try:
        bot_username = community.account.username
    except:
        return
    
    helper_message = get_helper_message(
        community,
        requestor_screen_name,
        bot_username, 
    )
    api = tweepy_api(username=helper_username)
    try:
        api.update_status(helper_message)
    except TweepError as e:
        logger.error(f"Error while trying to send the helper status: {e}")

def get_helper_message(community, requestor_screen_name, bot_username):
    db_message = community.helper_message
    if not db_message:
        return
    url = f"{site_url(community)}/oauth/login/twitter/?next={reverse('moderation:self')}"
    context = {
        'requestor': requestor_screen_name,
        'bot': bot_username,
        'url': url,
    }
    db_template = Template(db_message)
    return db_template.render(Context(context))