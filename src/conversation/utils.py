import logging

from django.core.paginator import Paginator

from conversation.constants import HOURS

logger = logging.getLogger(__name__)

def normalize(statusid):
    hashtag(statusid)
    retweetedstatus(statusid)
    quotedstatus(statusid)
    
def allnormalize():
    from .models import Tweetdj
    from .constants import TWEETDJ_PAGINATION
    paginator = Paginator(Tweetdj.objects.all(), TWEETDJ_PAGINATION)
    
    for page_idx in paginator.page_range:
        for row in paginator.page(page_idx).object_list:
            statusid = row.statusid
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
    
    keyword_lst = getConfig()["keyword_track_list"]
    if not keyword_lst:
        return
    status_mi = Tweetdj.objects.get(pk=statusid)
    if (status_mi.hashtag0 is not None) and (status_mi.hashtag1 is not None):
        return
    
    # remove hashtag character (#)
    for idx, keyword in enumerate(keyword_lst):
        keyword_lst[idx] = keyword[1:]
    jsn = status_mi.json
    key = "hashtags"
    contains_tag0 = False
    contains_tag1 = False
    for hashtags in dictextract(key, jsn):
        for hashtag in hashtags:
            contains_tag0 = contains_tag0 or bool(hashtag["text"].lower() == keyword_lst[0])
            if len(keyword_lst) > 1:
                contains_tag1 =  contains_tag1 or bool(hashtag["text"].lower() == keyword_lst[1])
    status_mi.hashtag0 = contains_tag0
    status_mi.hashtag1 = contains_tag1
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
    if userid is None:
        return
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
    if userid is None:
        return
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
    
def add_leaves(statusid):
    from django.db import transaction
    from .tree.tweet_server import request_context, request_tweets
    from .models import Treedj, create_leaf
    context = request_context(statusid)
    if not context:
        return
    for lst in context.descendants:
        for status in lst:
            tweet_context = request_tweets(status)
            if tweet_context is None:
                continue
            if tweet_context.in_reply_to_status_id:
                try:
                    parent = Treedj.objects.get(statusid=tweet_context.in_reply_to_status_id)
                except Treedj.DoesNotExist:
                    continue
                if parent:
                    with transaction.atomic():
                        leaf, created = Treedj.objects.get_or_create(statusid=tweet_context.tweet.statusid, parent=parent)
            if not tweet_context.descendants:
                continue
            
def feed_tree(statusid):
    from .models import Treedj
    from django.db.models import F
    try:
        root = Treedj.objects.get(statusid=statusid)
    except Treedj.DoesNotExist:
        return
    add_leaves(statusid)
    root.refresh_from_db()
    leaves_qs = root.get_descendants(include_self=True)
    logger.debug(leaves_qs.count())
    for leaf in leaves_qs:
        logger.debug(leaf.statusid)
        add_leaves(leaf.statusid)

def count_replies(statusid):
    from .models import Treedj
    try:
        root = Treedj.objects.get(statusid=statusid)
    except Treedj.DoesNotExist:
        return
    return root.get_descendant_count()
    
def count_replies_from_others(statusid):
    from .models import Treedj, Tweetdj
    from bot.addstatusdj import addstatus_if_not_exist, addstatus
    
    try:
        root = Treedj.objects.get(statusid=statusid)
    except Treedj.DoesNotExist:
        return
    
    total = root.get_descendant_count()
    
    try:
        root_tweetdj_mi = Tweetdj.objects.get(statusid=statusid)
    except Tweetdj.DoesNotExist:
        addstatus(statusid)
        root_tweetdj_mi = Tweetdj.objects.get(statusid=statusid)
    root_userid = root_tweetdj_mi.userid
    
    nodes_qs = root.get_descendants()
    nodes_statusid_lst = [node_mi.statusid for node_mi in nodes_qs]
    
    addstatus_if_not_exist(nodes_statusid_lst)
    
    own = Tweetdj.objects.filter(statusid__in=nodes_statusid_lst).filter(userid=root_userid).count()
    
    return total - own

def update_trees(hourdelta):
    """Update the trees created during the last hourdelta hours.
    
    timedelta -- int representing a time delta in hours
    """
    from datetime import datetime, timedelta
    from .models import Tweetdj, Treedj
    
    since = datetime.utcnow() - timedelta(hours=hourdelta)
    sid_status_lst = list(Tweetdj.objects.filter(created_at__gt=since).values_list('statusid', flat=True))
    sid_status_lst = sorted(sid_status_lst)
    try:
        oldest_status = sid_status_lst[0]
    except IndexError:
        return
    sid_tree_lst = list(Treedj.objects.filter(statusid__gte=oldest_status).values_list('statusid', flat=True))
    sid_tree_lst = sorted(sid_tree_lst, reverse=True)
    for sid in sid_tree_lst:
        feed_tree(sid)
        
def top_statusid_lst(hourdelta):
    """Return all tweets of the last hourdelta hours in order of most total replies.
    
    hourdelta -- int representing the number of hour(s)
    """
    from datetime import datetime, timedelta
    from .models import Tweetdj, Treedj
    from moderation.models import SocialUser
    
    since = datetime.utcnow() - timedelta(hours=hourdelta)
    tweet_sid_lst = list(Tweetdj.objects.filter(created_at__gt=since)
                         .filter(hashtag0=True)
                         .filter(userid__in=SocialUser.objects.authorized_users())
                         .values_list('statusid', flat=True))
    qs = Treedj.objects.filter(statusid__in=tweet_sid_lst)
    qs = [mi for mi in qs if mi.is_root_node()]
    top_lst = [(mi.statusid, mi.get_descendant_count()) for mi in qs]
    top_lst = sorted(top_lst, key=lambda x: x[1], reverse=True)
    return [t[0] for t in top_lst]

def help_statusid_lst(hourdelta):
    """Return all tweets of the last hourdelta hours in order of least other replies.
    
    number -- int
    hourdelta -- int representing the number of hour(s)
    """
    from datetime import datetime, timedelta
    from .models import Tweetdj, Treedj
    from moderation.models import SocialUser
    
    since = datetime.utcnow() - timedelta(hours=hourdelta)
    tweet_sid_lst = list(Tweetdj.objects
                         .filter(created_at__gt=since)
                         .filter(hashtag0=True)
                         .filter(userid__in=SocialUser.objects.authorized_users())
                         .values_list('statusid', flat=True))
    qs = Treedj.objects.filter(statusid__in=tweet_sid_lst)
    qs = [mi for mi in qs if mi.is_root_node()]
    help_lst = [(mi.statusid, count_replies_from_others(mi.statusid)) for mi in qs]
    help_lst = sorted(help_lst, key=lambda x: x[1])
    return [t[0] for t in help_lst]

def last_authorized_statusid_lst(hourdelta=None):
    """Return all tweets of interest (that contain hashtag0 & are root nodes)
    from the import last hourdelta hours
    """
    from datetime import datetime, timedelta
    from .models import Tweetdj, Treedj
    from moderation.models import SocialUser
    
    if hourdelta is None:
        hourdelta = HOURS
    
    since = datetime.utcnow() - timedelta(hours=hourdelta)
    tweet_sid_lst = list(Tweetdj.objects
                         .filter(created_at__gt=since)
                         .filter(hashtag0=True)
                         .filter(userid__in=SocialUser.objects.authorized_users())
                         .values_list('statusid', flat=True))
    qs = Treedj.objects.filter(statusid__in=tweet_sid_lst)
    qs = [mi for mi in qs if mi.is_root_node()]
    last_lst = [mi.statusid for mi in qs]
    last_lst = sorted(last_lst, reverse=True)
    return last_lst