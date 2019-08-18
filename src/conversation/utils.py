import logging

from django.core.paginator import Paginator
from django.db import connection, Error
from django.db.utils import IntegrityError
from django.conf import settings
from conversation.models import Tweetdj, Hashtag
from common.twitter import status_url_from_id

from conversation.constants import HOURS

logger = logging.getLogger(__name__)

def normalize(statusid):
    hashtag(statusid)
    hashtag_m2m(statusid)
    retweetedstatus(statusid)
    quotedstatus(statusid)
    
def allnormalize():
    from .models import Tweetdj
    from .constants import TWEETDJ_PAGINATION
    paginator = Paginator(Tweetdj.objects.all(), TWEETDJ_PAGINATION)
    
    for page_idx in paginator.page_range:
        for row in paginator.page(page_idx).object_list:
            statusid = row.statusid
            normalize(statusid)

def retweetedstatus(statusid):
    from common.utils import dictextract
    from .models import Tweetdj
    
    key = "retweeted_status"
    try:
        status_mi = Tweetdj.objects.get(pk=statusid)
    except Tweetdj.DoesNotExist as e:
        logger.error(e)
        return
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
    try:
        status_mi = Tweetdj.objects.get(pk=statusid)
    except Tweetdj.DoesNotExist as e:
        logger.error(e)
        return
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
    from .models import Tweetdj
    from common.utils import dictextract

    logger = logging.getLogger(__name__)
    
    keyword_lst = settings.KEYWORD_TRACK_LIST
    if not keyword_lst:
        return
    try:
        status_mi = Tweetdj.objects.get(pk=statusid)
    except Tweetdj.DoesNotExist as e:
        logger.info(f"Status {statusid} does not exist in table Tweetdj."
                    f"Error message: {e}")
        return
    
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

def hashtag_m2m(statusid: int):
    logger = logging.getLogger(__name__)
    try:
        status_mi = Tweetdj.objects.get(pk=statusid)
    except Tweetdj.DoesNotExist as e:
        logger.info(f"Status {statusid} does not exist in table Tweetdj."
                    f"Error message: {e}")
        return
    
    hashtag_m2m_tweetdj(status_mi) 

def hashtag_m2m_tweetdj(status_mi: Tweetdj):
    from common.utils import dictextract
    jsn = status_mi.json
    key = "hashtags"

    keyword_lst = Hashtag.objects.values_list("hashtag", flat=True)
    if not keyword_lst:
        return

    keyword_lst_lower = [keyword.lower() for keyword in keyword_lst]

    hash_dct = dict()
    for h in Hashtag.objects.all():
        hash_dct[h.hashtag.lower()]= h

    hashtag_mi_lst = []
 
    for hashtags in dictextract(key, jsn):
        for hashtag in hashtags:
            status_hashtag = hashtag["text"].lower()
            if status_hashtag in keyword_lst_lower:
                hashtag_mi = hash_dct[status_hashtag]
                hashtag_mi_lst.append(hashtag_mi)
    
    for h in hashtag_mi_lst:
        try:
            status_mi.hashtag.add(h)
        except IntegrityError:
            continue
                      
def allhashtag():
    from conversation.models import Tweetdj
    for status_mi in Tweetdj.objects.all():
        hashtag(status_mi.statusid)
        hashtag_m2m(status_mi.statusid)
        
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
    if userid is None:
        return
    total_count = 0
    for idx in range(len(settings.KEYWORD_TRACK_LIST)):
        count = userhashtagcount(userid, idx)
        if count:
            total_count += count
    return total_count
        
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
    page = requests.get(url=status_url_from_id(statusid), headers=headers)
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
    screen_name = screen_name(statusid)
    context = request_context(statusid, screen_name)
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
    TODO: scrap this
    selects statuses that contain hashtag0 but some
    root tweets don't contain the hashtag, which can be further down in the
    thread
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

def screen_name(statusid):
    """
    Get Twitter screen_name from statusid.
    TODO: Improve by fetching screen_name from the last status corresponding
    to the userid in order to avoid obsolete screen_name?
    Requires 3 queries: benchmark this.
    """
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT json -> 'user' ->> 'screen_name' from conversation_tweetdj where statusid = %s", [statusid])
        except Error as e:
            err_msg = f'''Error while retrieving screen_name for status 
                      {statusid}: {str(e)}'''
            logger.error(err_msg)
            return
        row = cursor.fetchone()
    if row:
        return row[0]
    
