import logging
from datetime import datetime
import pytz
logger = logging.getLogger(__name__)

def get_datetime(json) -> datetime:
    """ Returns the UTC creation datetime of the status as a Python object.

    "created_at":"Thu Apr 06 15:24:15 +0000 2017"
    
    """
    datetime_string = json["created_at"]
    return datetime.strptime(datetime_string, "%a %b %d %H:%M:%S +0000 %Y")

def get_datetime_tz(json) -> datetime:
    """ Returns the UTC creation datetime of the status as a Python object.

    "created_at":"Thu Apr 06 15:24:15 +0000 2017"
    
    """
    try:
        datetime_string = json["created_at"]
    except KeyError as e:
        logger.error(f"Key 'created_at' not found in json object. {e}")
        return
    return get_datetime_tz_from_twitter_str(datetime_string)

def get_datetime_tz_from_twitter_str(created_at: str) -> datetime:
    datetime_with_tz = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
    datetime_in_utc = datetime_with_tz.astimezone(pytz.utc)
    return datetime_in_utc

def datetime_twitter_str(datetime) -> str:
    return datetime.strftime('%a %b %d %H:%M:%S +0000 %Y')