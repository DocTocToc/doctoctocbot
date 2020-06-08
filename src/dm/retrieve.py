import logging
import time

from dm.api import getdm
from dm.models import DirectMessage
from community.models import Community
from django.db.utils import DatabaseError

logger = logging.getLogger(__name__)

def savedm():
    # Determine id of latest DM present in DM table
    for community in Community.objects.filter(active=True):
        userid = community.account.userid
        bot_screen_name = community.account.username
        lastids = list(
            DirectMessage.objects
            .filter(recipient_id=userid)
            .values_list("id", flat=True)
        )[:50]
        #logger.debug(f"lastids_mi: {lastids_mi}")
        #logger.debug(f"lastids: {lastids}")
        #logger.debug(f"lastids[0]: {lastids[0]}")
        #logger.debug(f"type of lastids[0]: {type(lastids[0])}")
        dms = getdm(bot_screen_name)
        if not dms:
            continue
        for dm in dms:
            dm_id = int(dm.id)
            if dm_id in lastids:
                continue
            if not DirectMessage.objects.filter(id=dm_id).exists():
                createdm(dm)
                #logger.debug(f'created new record for {dm["id"]} text:{dm.message_create["message_data"]["text"]}')
        time.sleep(60)
        
def createdm(dm):
    _id = int(dm.id)
    _created_timestamp = int(dm.created_timestamp)
    _sender_id = int(dm.message_create["sender_id"])
    _recipient_id = int(dm.message_create["target"]["recipient_id"])
    try:
        _source_app_id = int(dm.message_create.get("source_app_id"))
    except TypeError:
        _source_app_id = None
    _text = dm.message_create["message_data"]["text"]
    _jsn = dm.message_create["message_data"]
    try:
        DirectMessage.objects.create(
            id = _id,
            created_timestamp = _created_timestamp,
            sender_id = _sender_id,
            recipient_id = _recipient_id,
            source_app_id = _source_app_id,
            text = _text,
            jsn = _jsn,
        )
    except DatabaseError:
        pass