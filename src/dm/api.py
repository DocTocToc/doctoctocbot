import json
from .pythontwitter import twitter
from bot.models import Account
import logging
import typing

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

def getdm(dmid, screen_name):
    dm_lst = []
    count = 49
    cursor = -1
    api_ = getapi(screen_name)
    if not api_:
        return
    while True:
        logger.debug('client cursor:{}'.format(cursor))
        dms = api_.GetAllDirectMessages(count=count, cursor=cursor)
        dm_lst.extend(dms["events"])
        lcall= len(dms["events"])
        logger.debug(f'number of DMs returned during this call: {lcall}')
        logger.debug(f'total number of DMs returned so far: {len(dm_lst)}')
        cursor = dms.get("next_cursor", 0)
        logger.debug('client cursor:{}'.format(cursor))
        #list all ids in this api call result, stop if id is among them
        ids = []
        for dm in dms["events"]:
            ids.append(int(dm["id"]))
        if cursor == 0 or dmid in ids:
            break
    return dm_lst

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
        response = api_.PostDirectMessage(text=text,
                           user_id=user_id,
                           return_json=True,
                           quick_reply=quick_reply,
                           attachment=attachment)
    except twitter.error.TwitterError as e:
        logger.error("message_create event (DM) error: %s", e)
        response = str(e)
    
    logger.debug(response)

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