from .pythontwitter import twitter
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

def getapi():                                           
    api_dict = {'sleep_on_rate_limit': True}                                                      
    api_dict['consumer_key'] = settings.BACKEND_TWITTER_CONSUMER_KEY
    api_dict['consumer_secret'] = settings.BACKEND_TWITTER_CONSUMER_SECRET
    api_dict['access_token_key'] = settings.BACKEND_TWITTER_ACCESS_TOKEN
    api_dict['access_token_secret'] = settings.BACKEND_TWITTER_ACCESS_TOKEN_SECRET
    
    return twitter.Api(**api_dict)

def getdm(dmid):
    dm_lst = []
    count = 49
    cursor = -1
    api_ = getapi()
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
           attachment=None):
    api_ = getapi()
    try:
        response = api_.PostDirectMessage(text=text,
                           user_id=user_id,
                           return_json=True,
                           quick_reply=quick_reply,
                           attachment=attachment)
    except twitter.error.TwitterError as e:
        logger.error("message_create event (DM) error: %s", e)
        return False
    
    logger.debug(response)

    try:
        response["event"]["created_timestamp"]
    except KeyError:
        logger.error("Unknown message_create event (DM) error")
        return False

    id = response["event"]["message_create"]["target"]["recipient_id"]
    txt = response["event"]["message_create"]["message_data"]["text"]
    msg = f"Sending DM '{txt}' to user_id {id} was successful"
    logger.info(msg)
    return True