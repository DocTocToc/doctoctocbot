from moderation.models import SocialUser, Follower, Category
from bot.twitter import get_api
from django.db.utils import DatabaseError
import logging

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
  
    graph_dct = {}
    sum = 0
    
    for cat in categories:

        cat_ids = SocialUser.objects.category_users(cat)
        cat_cnt = intersection_count(cat_ids, followers)
        cat_dct = {cat: cat_cnt}
        graph_dct.update(cat_dct)
        sum += cat_cnt
    others = followers_cnt - sum
    graph_dct.update({'others': others})
    
    return graph_dct

def intersection_count(a, b):
    return len(set(a) & set(b))    
    
