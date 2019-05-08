from moderation.models import SocialUser, Follower, Category
from bot.twitter import get_api
from django.db.utils import DatabaseError
import logging
import numpy as np
import matplotlib.pyplot as plt
import io
import tempfile
from dm.api import senddm
from moderation.profile import screen_name
from django.utils.translation import gettext as _
from collections import OrderedDict
import operator
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone, translation

logger = logging.getLogger(__name__)

def get_socialuser(user):
    if isinstance(user, SocialUser):
        return user
    elif isinstance(user, int):
        try:
            return SocialUser.objects.get(user_id=user)
        except SocialUser.DoesNotExist:
            return


def followersids(user):
    su = get_socialuser(user)
    if not su:
        return
    hourdelta = settings.FOLLOWER_TIMEDELTA_HOUR or 24
    datetime_limit = timezone.now() - timedelta(hours=hourdelta)
    try:
        fi = Follower.objects.filter(user=su).last()
    except Follower.DoesNotExist:
        fi = None
    
    try:
        ok = fi.created > datetime_limit
        if ok:
            return fi.followers
    except AttributeError:
        pass

    followersids = _followersids(su.user_id)
    
    try:
        Follower.objects.create(
            user = su,
            followers = followersids
        )
    except DatabaseError as e:
        logger.error(f"Database error while saving Followers of user.user_id: {e}")
        return
    
    return followersids

def _followersids(user_id):
    api = get_api()
    return api.followers_ids(user_id)

def graph(user):
    with translation.override(settings.TRANSLATION_OVERRIDE):
        try:
            categories = Category.objects.filter(socialgraph=True).values_list('name', 'color')
        except Category.DoesNotExist as e:
            logger.error(f"No category set to appear on social graph. Exception:{e}")
            return
    
        followers = followersids(user)
        if not followers:
            return
    
        followers_cnt = len(followers)
      
        graph_dct = OrderedDict(
            {
                "title": _("Followers"),
                "categories": {},
                "global": {}
            }
        )
        sum = 0
        categories_dct = {}
        
        for cat, color in categories:
    
            cat_ids = SocialUser.objects.category_users(cat)
            cat_cnt = intersection_count(cat_ids, followers)
            cat_dct = {cat: {"count": cat_cnt, "color": color}}
            categories_dct.update(cat_dct)
            sum += cat_cnt
        
        others = followers_cnt - sum
        global_dct = OrderedDict({_('Verified'): sum, _('Others'): others})
        
        #graph_dct["categories"].update(order_dict(categories_dct, reverse=True))
        graph_dct["categories"].update(
            OrderedDict(sorted(categories_dct.items(),
            key=lambda k: k[1]["count"],
            reverse=True)
            )
        )
    
        graph_dct["global"].update(global_dct)
        graph_dct.update({"total": followers_cnt})
        graph_dct.update({"screen_name": screen_name(user)})

    return graph_dct

def intersection_count(a, b):
    return len(set(a) & set(b))    

def pie_plot(dct):
    if not dct:
        return
    with translation.override(settings.TRANSLATION_OVERRIDE):
        def func(pct, allvals):
            absolute = int(pct/100.*np.sum(allvals))
            return "{:.1f}% ({:d})".format(pct, absolute)
        
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

def get_dm_media_id(file):
    api = get_api()
    res = api.media_upload(file.name, media_category="dm_image")
    file.close()
    return res.media_id
    
def send_graph_dm(user_id, dest_user_id, text=""):
    with translation.override(settings.TRANSLATION_OVERRIDE):
        user_screen_name = screen_name(user_id)
        file = pie_plot(graph(user_id))
        if not file:
            return False
        media_id = get_dm_media_id(file)
        attachment = {"type": "media",
                      "media": {
                          "id": media_id }
                      }
        if text:
            text = " " + text
        dm_text = (
            _("Social graph of user @{screen_name}.{txt}")
            .format(screen_name=user_screen_name, txt=(text))
        )
        return senddm(dm_text,
                      user_id=dest_user_id,
                      attachment=attachment)
        
def order_dict(dct, reverse=False):
    return OrderedDict(sorted(dct.items(), key=operator.itemgetter(1), reverse=reverse))
