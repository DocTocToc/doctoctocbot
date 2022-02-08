import json
from dm.pythontwitter import twitter
from bot.models import Account
import logging
import typing
from bot.tweepy_api import get_api as get_tweepy_api
from dm.models import DirectMessage

from django.db.models import Q
import tweepy
from tweepy import TweepError
from django.conf import settings

logger = logging.getLogger(__name__)

def get_api_dict(__screen_name: typing.Optional[str]=None):
    if not __screen_name:
        return
    try:
        account = Account.objects.get(username=__screen_name)
        consumer_key = account.backend_twitter_consumer_key
        consumer_secret = account.backend_twitter_consumer_secret
        access_token = account.backend_twitter_access_token
        access_token_secret = account.backend_twitter_access_token_secret
    except Account.DoesNotExist as e:
        logger.error(f"account with username {__screen_name} does not exist. \n {e}")
        return
    if (not consumer_key
        or not consumer_secret
        or not access_token
        or not access_token_secret):
        return
    api_dict = {'sleep_on_rate_limit': True}                                                      
    api_dict['consumer_key'] = consumer_key
    api_dict['consumer_secret'] = consumer_secret
    api_dict['access_token_key'] = access_token
    api_dict['access_token_secret'] = access_token_secret
    return api_dict

def getapi(__screen_name: typing.Optional[str]=None):
    api_dict = get_api_dict(__screen_name)
    if api_dict:    
        return twitter.Api(**api_dict)

def getdm(bot_screen_name, bot_user_id: int):
    count=50
    api = get_tweepy_api(username=bot_screen_name, backend=True)
    if not api:
        return
    dm_id_lst = list(
        DirectMessage.objects.filter(
            Q(sender_id=bot_user_id) | Q(recipient_id=bot_user_id)    
        ).values_list("id", flat=True)
    )
    dm_lst = []
    try:
        for dm in tweepy.Cursor(api.list_direct_messages, count=count).items():
            if int(dm.id) in dm_id_lst:
                return dm_lst
            dm_lst.append(dm)
    except TweepError as e:
        logger.error(f'{e}')
    return dm_lst

def senddm_tweepy(
        text,
        recipient_id,
        quick_reply_type=None,
        attachment_type=None,
        attachment_media_id=None,
        screen_name=None
    ):
    api = get_tweepy_api(screen_name)
    if not api:
        return
    try:
        response = api.send_direct_message(
            recipient_id,
            text,
            quick_reply_type=quick_reply_type,
            attachment_type=attachment_type,
            attachment_media_id=attachment_media_id,
        )
        logger.debug(f"{response=} {type(response)=}")
        return response
    except twitter.error.TwitterError as e:
        logger.error("message_create event (DM) error: %s", e)
        return e

def senddm(text,
           user_id=None,
           return_json=True,
           quick_reply=None,
           attachment=None,
           screen_name=None):
    api_ = getapi(screen_name)
    if not api_:
        return
    try:
        response = api_.PostDirectMessage(
            text=text,
            user_id=user_id,
            return_json=True,
            quick_reply=quick_reply,
            attachment=attachment,
        )
    except twitter.error.TwitterError as e:
        logger.error("message_create event (DM) error: %s", e)
    
    try:
        response["event"]["created_timestamp"]
    except KeyError:
        """
        {'errors': [{'code': 349, 'message': 'You cannot send messages to this user.'}]}
        """
        try:
            error_msg = json.dumps(response)
        except:
            error_msg = "Unknown message_create event (DM) error"
        
        logger.error(error_msg)
        return error_msg

    userid = response["event"]["message_create"]["target"]["recipient_id"]
    txt = response["event"]["message_create"]["message_data"]["text"]
    if screen_name:
        account = f"@{screen_name}"
    else:
        account =  "default account"
    msg = f"Sending DM '{txt}' to user_id {userid} from {account} was successful"
    logger.info(msg)
    return response