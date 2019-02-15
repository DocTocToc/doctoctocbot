import logging

from bot.log.log import setup_logging
from dm.api import getdm
from dm.models import DirectMessage


setup_logging()
logger = logging.getLogger(__name__)

def savedm():
    # Determine id of latest DM present in DM table
    lastids_mi = DirectMessage.objects.all()[:49]
    #logger.debug(f"lastids_mi: {lastids_mi}")
    lastids = []
    for mi in lastids_mi:
        #logger.debug(mi)
        lastids.append(mi.id) 
    #logger.debug(f"lastids: {lastids}")
    if not lastids:
        lastids.append(0)
    #logger.debug(f"lastids[0]: {lastids[0]}")
    #logger.debug(f"type of lastids[0]: {type(lastids[0])}")
    for dm in getdm(lastids[0]):
        #logger.debug(f'dm: {dm["message_create"]["message_data"]["text"]}')
        #logger.debug(f"type of dm: {type(dm)}")
        if int(dm["id"]) in lastids:
            continue
        try:
            #logger.debug(f'dm["id"]: {dm["id"]}')
            #logger.debug(f'type(dm["id"]): {type(dm["id"])}')
            #logger.debug(f'int(dm["id"]): {int(dm["id"])}')
            #logger.debug(f'type(int(dm["id"])): {type(int(dm["id"]))}')
            DirectMessage.objects.get(id=int(dm["id"]))
        except DirectMessage.DoesNotExist:
            #logger.debug(f'Type of dm: {type(dm)}, dm id: {dm["id"]} text:{dm["message_create"]["message_data"]["text"]}')
            DirectMessage.objects.createdm(kwargs=dm)
            #logger.debug(f'created new record for {dm["id"]} text:{dm["message_create"]["message_data"]["text"]}')