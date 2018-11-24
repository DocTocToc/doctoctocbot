import logging

logger = logging.getLogger(__name__)

def normalize(statusid):
    hashtag(statusid)
    retweetedstatus(statusid)
    quotedstatus(statusid)
    
def allnormalize():
    from .models import Tweetdj
    for status_mi in Tweetdj.objects.all():
        statusid = status_mi.statusid
        hashtag(statusid)
        retweetedstatus(statusid)
        quotedstatus(statusid)

def retweetedstatus(statusid):
    from common.utils import dictextract
    from .models import Tweetdj
    
    key = "retweeted_status"
    status_mi = Tweetdj.objects.get(pk=statusid)
    if status_mi.retweetedstatus is not None:
        return status_mi.retweetedstatus
    
    status_mi.retweetedstatus = bool(next(dictextract(key, status_mi.json), None))
    status_mi.save()
    return status_mi.retweetedstatus
        
def allretweetedstatus():
    from .models import Tweetdj
    for status_mi in Tweetdj.objects.all():
        quotedstatus(status_mi.statusid)

def quotedstatus(statusid):
    from common.utils import dictextract
    from .models import Tweetdj
    
    key = "quoted_status"
    status_mi = Tweetdj.objects.get(pk=statusid)
    if status_mi.quotedstatus is not None:
        return status_mi.quotedstatus
    
    status_mi.quotedstatus = bool(next(dictextract(key, status_mi.json), None))
    status_mi.save()
    return status_mi.quotedstatus
        
def allquotedstatus():
    from .models import Tweetdj
    for status_mi in Tweetdj.objects.all():
        quotedstatus(status_mi.statusid)    

def hashtag(statusid):
    import logging
    from bot.conf.cfg import getConfig
    from .models import Tweetdj
    from common.utils import dictextract

    logger = logging.getLogger(__name__)
    
    logger.debug("hello")
    keyword_lst = getConfig()["keyword_track_list"]
    if not keyword_lst:
        return
    logger.debug("hello there")
    status_mi = Tweetdj.objects.get(pk=statusid)
    if (status_mi.hashtag0 is not None) and (status_mi.hashtag1 is not None):
        return
    
    logger.debug("hello down there")
    # remove hashtag character (#)
    for idx, keyword in enumerate(keyword_lst):
        keyword_lst[idx] = keyword[1:]
    #logger.debug(f"keyword_lst: {keyword_lst}")
    jsn = status_mi.json
    key = "hashtags"
    for hashtags in dictextract(key, jsn):
        logger.debug(hashtags)
        for hashtag in hashtags:
            logger.debug(hashtag)
            if not hashtag:
                continue
            logger.debug(hashtag["text"])
            if (hashtag["text"].lower() in keyword_lst):
                if len(keyword_lst) > 0:
                    status_mi.hashtag0 = bool(hashtag["text"].lower() == keyword_lst[0])
                    status_mi.save()
                if len(keyword_lst) > 1:
                    status_mi.hashtag1 = bool(hashtag["text"].lower() == keyword_lst[1])
                    status_mi.save()
                        
def allhashtag():
    from .models import Tweetdj
    for status_mi in Tweetdj.objects.all():
        hashtag(status_mi.statusid)
        
def userhashtagcount(userid, idx):
    from .models import Tweetdj
    if idx == 0:
            return Tweetdj.objects.filter(userid=userid).filter(hashtag0=True).count()
    elif idx == 1:
            return Tweetdj.objects.filter(userid=userid).filter(hashtag1=True).count()

def usertotalhashtagcount(userid):
    from bot.conf.cfg import getConfig
    count = 0
    for idx in range(len(getConfig()["keyword_track_list"])):
        count += userhashtagcount(userid, idx)
    return count

def gethashtag(idx):
    from bot.conf.cfg import getConfig
    keyword_lst = getConfig()["keyword_track_list"]
    try:
        return keyword_lst[idx]
    except IndexError:
        logger.error(f'Index {idx} caused an IndexError')