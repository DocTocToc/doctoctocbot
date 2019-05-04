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
    try:
        categories = Category.objects.filter(socialgraph=True).values_list('name', flat=True)
    except Category.DoesNotExist as e:
        logger.error(f"No category set to appear on social graph. Exception:{e}")
        return

    followers = followersids(user)
    if not followers:
        return

    followers_cnt = len(followers)
  
    graph_dct = OrderedDict({"categories": {}, "global": {}})
    sum = 0
    categories_dct = {}
    global_dct = {}
    
    for cat in categories:

        cat_ids = SocialUser.objects.category_users(cat)
        cat_cnt = intersection_count(cat_ids, followers)
        cat_dct = {cat: cat_cnt}
        categories_dct.update(cat_dct)
        sum += cat_cnt
    
    others = followers_cnt - sum
    global_dct = OrderedDict({'categories': sum, 'others': others})
    
    graph_dct["categories"].update(order_dict(categories_dct, reverse=True))
    graph_dct["global"].update(global_dct)
    return graph_dct

def intersection_count(a, b):
    return len(set(a) & set(b))    

def pie_plot(dct):
    def func(pct, allvals):
        absolute = int(pct/100.*np.sum(allvals))
        return "{:.1f}% ({:d})".format(pct, absolute)
    
    fig, ax = plt.subplots(1, 2, figsize=(24, 12), subplot_kw=dict(aspect="equal"))

    dct_cat = dct["categories"]
    dct_glob = dct["global"]

    labels1 = list(dct_cat.keys())
    labels2 = list(dct_glob.keys())
    
    data1 = list(dct_cat.values())
    data2 = list(dct_glob.values())

    wedges, texts, autotexts  = ax[0].pie(data1,
                                          autopct=lambda pct: func(pct, data1),
                                          textprops=dict(color="w"),
                                          startangle=0)
    
    ax[0].legend(wedges,
                 labels1,
                 title="Catégories",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1))
    
    wedges, texts, autotexts  = ax[1].pie(data2,
                                          autopct=lambda pct: func(pct, data2),
                                          textprops=dict(color="w"),
                                          startangle=0)
    
    ax[1].legend(wedges,
                 labels2,
                 title="Catégories",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1))
    
    plt.setp(autotexts, size=12, color='black')

    ax[0].set_title(_("Professions of verified followers"))
    ax[1].set_title(_("Share of verified followers"))

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
    
def send_graph_dm(user_id, dest_user_id):
    user_screen_name = screen_name(user_id)
    file = pie_plot(graph(user_id))
    media_id = get_dm_media_id(file)
    attachment = {"type": "media",
                  "media": {
                      "id": media_id }
                  }
    dm_text = _("Social graph of user {screen_name}").format(screen_name=user_screen_name)
    senddm(dm_text,
           user_id=dest_user_id,
           attachment=attachment)
    
def order_dict(dct, reverse=False):
    return OrderedDict(sorted(dct.items(), key=operator.itemgetter(1), reverse=reverse))
