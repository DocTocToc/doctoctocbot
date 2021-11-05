import logging

from django.core.paginator import Paginator
from django.db import connection, Error
from django.db.utils import IntegrityError, DatabaseError
from django.conf import settings
from conversation.models import Tweetdj, Hashtag, Treedj
from common.twitter import status_url_from_id
from common.utils import dictextract
from timeline.models import last_retweeted_statusid_lst
from conversation.constants import HOURS
from community.helpers import get_community

logger = logging.getLogger(__name__)

def normalize(statusid):
    hashtag_m2m(statusid)
    retweetedstatus(statusid)
    quotedstatus(statusid)
    
def allnormalize():
    from .constants import TWEETDJ_PAGINATION
    paginator = Paginator(Tweetdj.objects.all(), TWEETDJ_PAGINATION)
    
    for page_idx in paginator.page_range:
        for row in paginator.page(page_idx).object_list:
            statusid = row.statusid
            normalize(statusid)

def retweetedstatus(statusid):
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
    for status_mi in Tweetdj.objects.all():
        quotedstatus(status_mi.statusid)

def quotedstatus(statusid):
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
    for status_mi in Tweetdj.objects.all():
        quotedstatus(status_mi.statusid)    

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
        except DatabaseError as e:
            logger.error(e)
            continue
                      
def allhashtag():
    for status_mi in Tweetdj.objects.all():
        hashtag_m2m(status_mi.statusid)
        
def userhashtagcount(userid: int, request) -> dict:
    """
    Return the count of status posted by the user with this userid for the following hashtags:
     - community hashtags
     - trusted communities hashtags
    that are neither retweets nor quotes.
    """
    if not userid or not request:
        return
    mi_lst = Tweetdj.objects.filter(
        userid=userid,
        quotedstatus=False,
        retweetedstatus=False
    )
    community = get_community(request)
    hashtag_lst = []
    hashtag_lst.extend(list(community.hashtag.all()))
    trusted_community_lst = community.trust.all()
    for community in trusted_community_lst:
        hashtag_lst.extend(community.hashtag.all())
    hashtag_lst = set(hashtag_lst)
    hashtag_dct = dict()
    for hashtag in hashtag_lst:
        hashtag_dct.update(
            {
                hashtag.hashtag: mi_lst.filter(hashtag=hashtag).count()
            }
        )
    return hashtag_dct

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
    _screen_name = screen_name(statusid)
    context = request_context(statusid, _screen_name)
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
                        _leaf, _created = Treedj.objects.get_or_create(statusid=tweet_context.tweet.statusid, parent=parent)
            if not tweet_context.descendants:
                continue
            
def feed_tree(statusid):
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
    try:
        root = Treedj.objects.get(statusid=statusid)
    except Treedj.DoesNotExist:
        return
    return root.get_descendant_count()
    
def count_replies_from_others(statusid):
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
        
def top_statusid_lst(hourdelta, community):
    """Return all tweets of the last hourdelta hours in order of most total replies.
    
    hourdelta -- int representing the number of hour(s)
    """
    from datetime import datetime, timedelta
    from moderation.models import SocialUser

    tweet_sid_lst = last_retweeted_statusid_lst(hourdelta, community)
    qs = Treedj.objects.filter(statusid__in=tweet_sid_lst)
    qs = [mi for mi in qs if mi.is_root_node()]
    top_lst = [(mi.statusid, mi.get_descendant_count()) for mi in qs]
    top_lst = sorted(top_lst, key=lambda x: x[1], reverse=True)
    return [t[0] for t in top_lst]

def help_statusid_lst(hourdelta, community):
    """Return all tweets of the last hourdelta hours in order of least other replies.
    
    number -- int
    hourdelta -- int representing the number of hour(s)
    """
    from datetime import datetime, timedelta
    from moderation.models import SocialUser

    tweet_sid_lst = last_retweeted_statusid_lst(hourdelta, community)
    qs = Treedj.objects.filter(statusid__in=tweet_sid_lst)
    qs = [mi for mi in qs if mi.is_root_node()]
    help_lst = [(mi.statusid, count_replies_from_others(mi.statusid)) for mi in qs]
    help_lst = sorted(help_lst, key=lambda x: x[1])
    return [t[0] for t in help_lst]

def screen_name(statusid):
    """
    Get Twitter user screen_name from statusid.
    TODO: Improve by fetching screen_name from the last status corresponding
    to the userid in order to avoid obsolete screen_name?
    Requires 3 queries: benchmark this.
    """
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT json -> 'user' ->> 'screen_name' from conversation_tweetdj where statusid = %s", [statusid])
        except Error as e:
            err_msg = f'''Error while retrieving user screen_name for status 
                      {statusid}: {str(e)}'''
            logger.error(err_msg)
            return
        row = cursor.fetchone()
    if row:
        screen_name= row[0]
        logger.debug(screen_name)
        return screen_name
    
def name(statusid):
    """
    Get Twitter user name from statusid.
    """
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT json -> 'user' ->> 'name' from conversation_tweetdj where statusid = %s", [statusid])
        except Error as e:
            err_msg = f'''Error while retrieving name of user for status 
                      {statusid}: {str(e)}'''
            logger.error(err_msg)
            return
        row = cursor.fetchone()
    if row:
        name= row[0]
        logger.debug(name)
        return name
    
def full_text(statusid):
    """
    Get Twitter full_text from statusid.
    """
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT json -> 'full_text' from conversation_tweetdj where statusid = %s", [statusid])
        except Error as e:
            err_msg = f'''Error while retrieving full_text for status 
                      {statusid}: {str(e)}'''
            logger.error(err_msg)
            return
        row = cursor.fetchone()
    if row:
        full_text= row[0]
        logger.debug(full_text)
        return full_text
    
def created_at(statusid):
    """
    Get Twitter created_at (date time creation string) from statusid.
    """
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT json ->> 'created_at' from conversation_tweetdj where statusid = %s", [statusid])
        except Error as e:
            err_msg = f'''Error while retrieving created_at for status 
                      {statusid}: {str(e)}'''
            logger.error(err_msg)
            return
        row = cursor.fetchone()
    if row:
        created_at= row[0]
        logger.debug(created_at)
        return created_at