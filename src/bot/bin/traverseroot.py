import logging
from conversation.models import Tweetdj
from ..addstatusdj import addstatus
from ..doctoctocbot import retweet, isquestion

logger = logging.getLogger(__name__)

def retweetroot(statusid: int):
    """
    Starting from the status with statusid, analyze nodes towards root to
    determine if the root status should be retweeted.
    Retweet only if all nodes leading to root have the same author and if they contain a question mark
    """
    logger.debug(type(statusid))
    status_mi: Tweetdj = getorcreate(statusid)
    logger.debug(status_mi.json['full_text'])
    logger.debug(status_mi.json['in_reply_to_status_id'])
    logger.debug(status_mi.parentid)
    if status_mi.parentid is None:
        return

    hasquestionmark: bool = isquestion(status_mi.json)
    logger.debug(f"hasquestionmark:{hasquestionmark}")
    authorid: int = status_mi.userid
    logger.debug(f"authorid:{authorid}")
    current_mi: Tweetdj = status_mi
    
    while True:
        
        parent_mi = getorcreate(current_mi.parentid)

        if parent_mi is None:
            break      
      
        if not hasquestionmark:
            hasquestionmark = isquestion(parent_mi.json)
            logger.debug(f"hasquestionmark:{hasquestionmark}")
        
        try:
            logger.debug(f"parent_mi.userid:{parent_mi.userid}") 
        except AttributeError:
            pass
        
        if not (parent_mi.userid == authorid):
            break
        if parent_mi.parentid is None:
            if hasquestionmark:
                retweet(parent_mi.statusid)
                break
            else:
                break
        
        current_mi = parent_mi
        
    return

def getorcreate(statusid: int) -> Tweetdj:    
    # Is status in database? If not, add it.
    if statusid is None:
        logger.debug("statusid is None.")
        return None
    try:
        return Tweetdj.objects.get(pk=statusid)
    except Tweetdj.DoesNotExist:
        addstatus(statusid)
        return Tweetdj.objects.get(pk=statusid)
    
    
    