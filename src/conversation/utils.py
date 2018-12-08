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
        
def userhashtagcount(userid: int, idx: int) -> int:
    """
    Return the count of status posted by the user with this userid including a given hashtag
    (according to its index in the configuration list) that are neither retweets nor quotes.
    """
    from .models import Tweetdj
    mi_lst = Tweetdj.objects.filter(userid=userid, quotedstatus=False, retweetedstatus=False)
    if idx == 0:
            return mi_lst.filter(hashtag0=True).count()
    elif idx == 1:
            return mi_lst.filter(hashtag1=True).count()

def usertotalhashtagcount(userid: int) -> int:
    """
    Return the count of status posted by the user with this userid, including any hashtag
    from the keyword track list, that are neither retweets nor quotes.
    """
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
        
def getcount(statusid):
    """
    Return a dictionary with reply, retweet and likes (favorite) counts from the web API.
    """
    import requests
    from lxml import html
    count = {"reply": None,
             "retweet": None,
             "favorite": None}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5"}
    page = requests.get(url=f'https://twitter.com/statuses/{statusid}', headers=headers)
    tree = html.fromstring(page.content)
    
    for k in count.keys():
        attval = f"profile-tweet-action-{k}-count-aria-{statusid}"
        xpath = f'//*[@id="{attval}"]'
        lst = tree.xpath(xpath)
        try:
            val_int = int(lst[0].text_content().split()[0])
        except IndexError:
            val_int = 0
        count[f'{k}'] = val_int
    return count

def updatecount(statusid):
    """
    Update Tweetdj status reply, retweet and like count with data collected from the web API.
    """
    from .models import Tweetdj
    try:
        mi = Tweetdj.objects.get(pk=statusid)
    except Tweetdj.DoesNotExist:
        return
    count = getcount(statusid)
    mi.reply=count["reply"]
    mi.retweet=count["retweet"]
    mi.like=count["favorite"]
    mi.save()
    
    
    