import pytz
import time
from typing import Optional
from moderation.models import SocialUser, Follower, Friend, Category
from bot.tweepy_api import get_api
from bot.models import Account
from django.db.utils import DatabaseError
import logging
import numpy as np
import matplotlib.pyplot as plt
import io
import tempfile
from dm.api import senddm
from moderation.profile import screen_name
from community.models import CommunityCategoryRelationship
from django.utils.translation import gettext as _
from collections import OrderedDict
import operator
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone, translation
from tweepy import TweepError
import tweepy
from django.core.exceptions import ObjectDoesNotExist
from PIL import Image
from django.core.files import File
from community.helpers import activate_language

logger = logging.getLogger(__name__)

def get_socialuser_from_user_id(user_id):
    """ Get a SocialUser object from its user_id"""
    try:
        return SocialUser.objects.get(user_id=user_id)
    except SocialUser.DoesNotExist:
        return
    
def get_socialuser_from_screen_name(screen_name):
    try:
        return SocialUser.objects.get(
            profile__json__screen_name=screen_name
        )
    except SocialUser.DoesNotExist:
        return

def get_socialuser(user):
    if isinstance(user, SocialUser):
        logger.debug("user is a SocialUser")
        return user
    elif isinstance(user, int):
        logger.debug("user is a int")
        return get_socialuser_from_user_id(user)
    elif isinstance(user, str):
        logger.debug("user is a string")
        return get_socialuser_from_screen_name(user)


# TODO: fix type to accept string for username
def update_social_ids(
        user,
        cached = False,
        bot_screen_name = None,
        relationship = None,
        delta: Optional[timedelta] = None,
    ):
    if relationship is None:
        return
    if not relationship in ['friends', 'followers']:
        logger.error(
            f"relationship parameter: {relationship} not "
            "['friends', 'followers']"
        )
        return
    if relationship == 'followers':
        followers = True
    else:
        followers = False
    su = get_socialuser(user)
    logger.debug(f"SocialUser: {su}")
    if not su:
        return
    cache_delta = timedelta()
    if delta:
        cache_delta = delta
    else:
        if followers:
            cache_delta = timedelta(hours=settings.FOLLOWER_TIMEDELTA_HOUR)
        else:
            cache_delta = timedelta(hours=settings.FRIEND_TIMEDELTA_HOUR)
    datetime_limit = datetime.now(pytz.utc) - cache_delta
    logger.debug(f"{datetime_limit}")

    if followers:
        try:
            si = Follower.objects.filter(user=su).last()
            if si:
                logger.debug(f"Followers id_list: {si.id_list}")
        except Follower.DoesNotExist:
            si = None
            logger.debug(f"Follower instance does not exist for user {su.user_id}")
    else:
        try:
            si = Friend.objects.filter(user=su).last()
        except Friend.DoesNotExist:
            logger.debug(f"Friend instance does not exist for {su.user_id}")
            si = None

    if settings.UPDATE_SOCIAL_IDS_FORCE_CACHE:
        if si:
            return si.id_list
        else:
            return []
    ok = False
    try:
        ok = si.created > datetime_limit and cached
    except AttributeError:
        pass

    if ok and si:
        return si.id_list

    if followers:
        usersids = _followersids(su.user_id, bot_screen_name)
    else:
        usersids = _friendsids(su.user_id, bot_screen_name)

    if usersids is None:
        return

    if followers:
        record_followersids(su, usersids)
    else:
        record_friendsids(su, usersids)

    return usersids

def record_followersids(su, usersids):
    try:
        Follower.objects.create(
            user = su,
            id_list = usersids
        )
    except DatabaseError as e:
        logger.error(f"Database error while saving Followers of user.user_id: {e}")

def record_friendsids(su, usersids):
    try:
        Friend.objects.create(
            user = su,
            id_list = usersids
        )
    except DatabaseError as e:
        logger.error(f"Database error while saving Friends of user.user_id: {e}")

def _followersids(user_id, bot_screen_name):
    api = get_api(bot_screen_name)
    followers_ids = []
    try:
        for page in tweepy.Cursor(
            api.followers_ids,
            user_id=user_id
            ).pages():
            logger.debug(f'{len(page)}')
            logger.debug(f'{page[:10]}')
            followers_ids.extend(page)
            #if len(page) == 5000:
            #    time.sleep(60)
        return followers_ids
    except TweepError as e:
        logger.error("Tweepy Error: %s", e)
    except AttributeError as e:
        logger.error(f"Attribute Error ({api =}): {e}")

def _friendsids(user_id, bot_screen_name):
    api = get_api(bot_screen_name)
    friends_ids = []
    try:
        for page in tweepy.Cursor(
            api.friends_ids,
            user_id=user_id
            ).pages():
            logger.debug(f'{len(page)}')
            logger.debug(f'{page[:10]}')
            friends_ids.extend(page)
            #if len(page) == 5000:
            #    time.sleep(60)
        return friends_ids
    except TweepError as e:
        logger.error("Tweepy Error: %s", e)
    except AttributeError as e:
        logger.error(f"Attribute Error ({api =}): {e}")

def graph(user_id, community, bot_screen_name):
    try:
        categories = CommunityCategoryRelationship.objects.filter(
            socialgraph=True,
            community=community
        ).values_list('category__name', 'color')
    except CommunityCategoryRelationship.DoesNotExist as e:
        logger.error(f"No category set to appear on social graph. Exception:{e}")
        return
    logger.debug(f"{categories}")
    logger.debug(f"{bot_screen_name}")

    followers = update_social_ids(
        user_id,
        cached=True,
        bot_screen_name=bot_screen_name,
        relationship='followers',
    )
    if not followers:
        logger.debug("No followers.")
        return
    
    logger.debug(f"{followers[0:10]}")

    followers_cnt = len(followers)
  
    graph_dct = OrderedDict(
        {
            "title": _("Followers"),
            "categories": None,
            "global": None,
        }
    )
    logger.debug(graph_dct)
    _sum = 0
    categories_dct = {}
    
    for cat, color in categories:
        cat_ids = SocialUser.objects.category_users(cat)
        cat_cnt = intersection_count(cat_ids, followers)
        cat_dct = {cat: {"count": cat_cnt, "color": color}}
        categories_dct.update(cat_dct)
        _sum += cat_cnt
    
    others = followers_cnt - _sum
    global_dct = OrderedDict({_('Verified'): _sum, _('Others'): others})
    
    #graph_dct["categories"].update(order_dict(categories_dct, reverse=True))
    graph_dct.update(
        {
            "categories": OrderedDict(
                sorted(
                    categories_dct.items(),
                    key=lambda k: k[1]["count"],
                    reverse=True
                )
            )
        }
    )

    graph_dct.update(
        {
            "global": global_dct
        }
    )
    graph_dct.update({"total": followers_cnt})
    graph_dct.update({"screen_name": screen_name(user_id)})
    graph_dct.update({"community": community})
    logger.debug(graph_dct)
    return graph_dct

def intersection_count(a, b):
    return len(set(a) & set(b))    

def pie_plot(dct):
    if not dct:
        return

    def func(pct, allvals):
        absolute = int(pct/100.*np.sum(allvals))
        return "{:.1f}% ({:d})".format(pct, absolute)
    
    activate_language(dct["community"])
    fig, ax = plt.subplots(2, 1, figsize=(6, 12), subplot_kw=dict(aspect="equal"))

    dct_cat = dct["categories"]
    dct_glob = dct["global"]

    labels1 = list(dct_cat.keys())
    labels2 = list(dct_glob.keys())
    
    data1 = [t["count"] for t in dct_cat.values()]
    colors1 = [t["color"] for t in dct_cat.values()]
    
    data2 = list(dct_glob.values())

    wedges, texts, autotexts  = ax[0].pie(data1,
                                          autopct=lambda pct: func(pct, data1),
                                          textprops=dict(color="w"),
                                          startangle=0,
                                          colors=colors1)
    
    ax[0].legend(wedges,
                 labels1,
                 title="Categories",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1))
    
    wedges, texts, autotexts  = ax[1].pie(data2,
                                          autopct=lambda pct: func(pct, data2),
                                          textprops=dict(color="w"),
                                          startangle=0)
    
    ax[1].legend(wedges,
                 labels2,
                 title=dct["title"],
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1))
    
    plt.setp(autotexts, size=12, color='black')

    ax[0].set_title(
        _("Categories of verified {title}").format(title = dct["title"])
    )
    ax[1].set_title(
        _("Share of verified {title}").format(title = dct["title"])
    )

    title_str = (
        _('{title} of {screen_name}: {total}')
        .format(
            title = dct["title"],
            screen_name=dct["screen_name"],
            total=dct["total"]
        )
    )
    fig.suptitle(title_str, fontsize=12)
    fig.subplots_adjust(top=0.88)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format = 'png')
    buffer.seek(0)
    f = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    f.write(buffer.read())
    buffer.close()
    f.close()
    return f

def get_dm_media_id(file, bot_screen_name):
    api = get_api(username=bot_screen_name, backend=True)
    logger.debug(api)
    try:
        res = api.media_upload(file.name, media_category="dm_image")
        file.close()
    except TweepError as e:
        logger.error("Tweepy Error: %s", e)
        file.close()
        return
    except AttributeError as e:
        logger.error(f"Attribute Error ({api =}): {e}")
        file.close()
        return
    except:
        file.close()
        return
    try:
        return res.media_id
    except AttributeError as e:
        logger.error(f"AttributeError: {e}")
    
    
def send_graph_dm(user_id, dest_user_id, bot_screen_name, text, community):
    activate_language(community)
    logger.debug("Inside send_graph_dm()")
    user_screen_name = screen_name(user_id)
    logger.debug(f"user_screen_name:{user_screen_name}")
    _graph = graph(user_id, community, bot_screen_name)
    if not _graph:
        logger.debug("_graph is Falsy")
        return 
    try:
        file = pie_plot(_graph)
    except:
        file = None

    if not file:
        logger.debug("file is Falsy")
        try:
            su = SocialUser.objects.get(user_id=user_id)
            if su.profile:
                normalavatar = su.profile.normalavatar
                logger.debug(normalavatar)
        except:
            logger.error("Error while processing profile")
            return False
        if normalavatar:
            try:
                file = open(normalavatar.path, 'rb')
            except:
                file = None
    if file:
        media_id = get_dm_media_id(file, bot_screen_name)
        logger.debug(f"media_id: {media_id}")
        if media_id:
            attachment = {
                "type": "media",
                "media": {
                    "id": media_id
                }
            }
    else:
        attachment = None
    if text:
        text = " " + text
    dm_text = (
        _("Social graph of user @{screen_name}.{txt}")
        .format(
            screen_name=user_screen_name,
            txt=text
        )
    )
    res = senddm(
        dm_text,
        user_id=dest_user_id,
        screen_name=bot_screen_name,
        attachment=attachment
    )
    logger.debug(f"res: {res}")
    return res
        
def order_dict(dct, reverse=False):
    return OrderedDict(sorted(dct.items(), key=operator.itemgetter(1), reverse=reverse))
