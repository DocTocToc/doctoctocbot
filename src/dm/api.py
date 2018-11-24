from .pythontwitter import twitter
from bot.conf.cfg import getConfig                                                                      
from bot.log.log import setup_logging
import logging

logger = logging.getLogger(__name__)

def getapi():                                           
    api_dict = {'sleep_on_rate_limit': True}                                                      
    api_dict['consumer_key'] = getConfig()["twitter"]["consumer_key"]
    api_dict['consumer_secret'] = getConfig()["twitter"]["consumer_secret"]
    api_dict['access_token_key'] = getConfig()["twitter"]["access_token"]
    api_dict['access_token_secret'] = getConfig()["twitter"]["access_token_secret"]
    
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
           quick_reply=None):
    api_ = getapi()
    api_.PostDirectMessage(text=text,
                           user_id=user_id,
                           return_json=True,
                           quick_reply=quick_reply)