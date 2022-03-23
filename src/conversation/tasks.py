import logging
import tweepy
import requests
import time
import gc
from random import shuffle
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from celery import shared_task
from constance import config
from pathlib import Path
from conversation.models import Retweeted, Tweetdj
from bot.models import Account
from bot.tweepy_api import get_api
from moderation.models import SocialUser
from conversation.utils import update_trees
from moderation.models import addsocialuser, Category
from community.models import Community
from conversation.timeline import community_timeline, user_id_list_timeline

logger = logging.getLogger(__name__)


@shared_task
def handle_normalize(statusid):
    from .utils import normalize
    normalize(statusid)
    

@shared_task(
    soft_time_limit=config.normalize_soft_time_limit,
    time_limit=config.normalize_time_limit
)
def handle_allnormalize():
    from .utils import allnormalize
    allnormalize()

@shared_task
def handle_update_trees(hourdelta):
    update_trees(hourdelta)

@shared_task
def handle_addsocialuser():
    for instance in Tweetdj.objects.all():
        addsocialuser(instance)

@shared_task
def update_retweet(days):
    """Update Retweeted and Tweetdj to reflect unretweets
    TODO: Doesn't work if the same tweet that was unretweeted is retweeted
    again.
    """
    start_datetime = timezone.now() - timedelta(days=days)
    count = 200
    for account in Account.objects.filter(active=True):
        api = get_api(username=account.username)
        if not api:
            continue
        start_tweetdj = (
            Tweetdj.objects
                .filter(socialuser__user_id=account.userid)
                .filter(created_at__gte=start_datetime)
                .last()
            )
        logger.debug(start_tweetdj)
        if not start_tweetdj:
            continue
        start_id = start_tweetdj.statusid
        timeline_status = []
        for status in tweepy.Cursor(api.user_timeline, 
                            user_id=account.userid, 
                            count=count,
                            since_id=start_id,
                            max_id=None,
                            trim_user=True,
                            exclude_replies=True,
                            include_retweets=True,
                            tweet_mode="extended",
                            ).items():
            timeline_status.append(status._json["id"])
        rt_status: List(int) = list(
            Retweeted.objects
            .filter(status__gte=start_id)
            .filter(account=account)
            .values_list("retweet", flat=True)
        )
        logger.debug(f"rt_status: {rt_status}")
        logger.debug(f"timeline_status: {timeline_status}")
        deleted = list(set(rt_status).difference(timeline_status))
        logger.debug(f"deleted: {deleted}")
        status_id = (
            Retweeted.objects
            .filter(retweet__in=deleted)
            .filter(account=account)
            .values_list('status', flat=True)
        )
        try:
            social_user = SocialUser.objects.get(user_id=account.userid)
        except SocialUser.DoesNotExist:
            social_user = None
        if social_user:
            for tweetdj in Tweetdj.objects.filter(statusid__in=status_id):
                tweetdj.retweeted_by.remove(social_user)
        
        for rt in Retweeted.objects.as_of().filter(retweet__in=deleted):
            rt.delete()
            
        for tweetdj in Tweetdj.objects.filter(statusid__in=deleted):
            if not tweetdj.deleted:
                tweetdj.deleted=True
                tweetdj.save()

@shared_task(
    soft_time_limit=config.timeline_soft_time_limit,
    time_limit=config.timeline_time_limit
)
def handle_community_members_timeline(community_name: str):
    try:
        community = Community.objects.get(name=community_name)
    except Community.DoesNotExist:
        logger.error(f"'{community_name}' does not exist.")
        return
    community_timeline(community)
    
@shared_task
def handle_category_timeline(category_name: str):
    try:
        category = Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        return
    user_id_list = category.twitter_id_list()
    shuffle(user_id_list)
    user_id_list_timeline(user_id_list)
   
@shared_task
def handle_image(url, filename):
    for name in ["thumb", "large"]:
        if name == "thumb":
            filepath = settings.BOT_IMAGES_THUMBNAILS_PATH + "/" + filename
        elif name == "large":
            filepath = settings.BOT_IMAGES_PATH + "/" + filename
        full_url = url + f"?name={name}"
        r = requests.get(full_url, allow_redirects=True)
        with open(filepath, 'wb') as f:
            f.write(r.content)
        file = Path(filepath)
        if file.is_file():
            logger.debug(f"{name} image %s written on disk." % filepath)
        else:
            logger.error(f"{name} image %s not found on disk." % filepath)

@shared_task
def handle_update_truncated_statuses(n):
    from bot.lib.statusdb import Addstatus
    from itertools import cycle

    def gen_api():
        qs = Account.objects.filter(active=True)
        api_lst = [get_api(account.username) for account in qs]
        for i in cycle(api_lst):
            yield i

    def gen():
        lst =  [1,2]
        for i in cycle(lst):
            yield i

    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    truncated_qs = Tweetdj.objects.filter(json__truncated=True)[:n]
    api_gen = gen_api()
    for chunk in chunks(truncated_qs, 100):
        API = next(api_gen)
        try:
            s_lst = API.statuses_lookup(
                [status.statusid for status in chunk],
                include_entities=True,
                tweet_mode='extended'
            )
        except tweepy.TweepError as e:
            logger.debug("Tweepy error: %s", e)
            return
        for tweet in s_lst:
            addstatus = Addstatus(tweet._json)
            addstatus.addtweetdj(update=True)

@shared_task
def handle_text_search_vector(statusid):
    from conversation.search.search_vector import TextSearchVector
    try:
        tweetdj=Tweetdj.objects.get(statusid=statusid)
    except Tweetdj.DoesNotExist:
        return
    tsv=TextSearchVector(tweetdj)
    tsv.update_status_text()

def queryset_iterator(queryset, chunksize=10000):
    counter = 0
    count = chunksize
    while count == chunksize:
        offset = counter - counter % chunksize
        count = 0
        for item in queryset.all()[offset:offset + chunksize]:
            count += 1
            yield item
        counter += count
        gc.collect()

@shared_task
def handle_all_text_search_vector(n):
    from conversation.search.search_vector import TextSearchVector
    tweetdj_set = (
        Tweetdj.objects
        .exclude(json__isnull=True)
        .exclude(json__has_key='retweeted_status')
        .filter(status_text__isnull=True)
        .filter(json__isnull=False)
        .filter(json__has_any_keys=['full_text', 'text'])
        .order_by('-statusid')
        [:n]
    )
    for tweetdj in queryset_iterator(tweetdj_set, chunksize=500):
        if tweetdj.status_text:
            continue
        tsv=TextSearchVector(tweetdj)
        tsv.update_status_text()
        if settings.DEBUG:
            tweetdj.refresh_from_db()
            try:
                txt = tweetdj.json["full_text"]
            except:
                try:
                    txt = tweetdj.json["text"]
                except:
                    txt = ""
            logger.debug(f'\n{tweetdj.statusid}\n{txt}\n{str(tweetdj.status_text)}\n\n')
        gc.collect()