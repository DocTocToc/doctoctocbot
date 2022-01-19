import logging
from typing import List
from conversation.models import Tweetdj
from constance import config

logger = logging.getLogger(__name__)

rt_ratio_limit = config.hive__utils__tweetsubscription_retweet_ratio

def is_retweeted_by_categories(
        tweetdj: Tweetdj,
        rt_target: int,
        category: List
    ):
    """Return True if socialusers from listed categories retweeted status
    at least rt_target times
    tweetdj: Tweetdj object
    rt_target: int
    category: list of Categories objects
    """
    category_set = set(category.values_list("id", flat=True))
    logger.debug(f"{category_set=}")
    all_rt_count = tweetdj.json["retweet_count"]
    rt_count = 0
    for su in tweetdj.retweeted_by.all():
        rt_count += len(
            set(su.category.values_list("id", flat=True)) & category_set
        )
    # Filter viral tweets
    try:
        rt_ratio = rt_count / all_rt_count
    except ZeroDivisionError:
        rt_ratio = None
    ok_ratio: bool = True
    if rt_ratio:
        ok_ratio = rt_ratio >= rt_ratio_limit
    logger.debug(
        f"{rt_count=} {rt_target=} {rt_count >= rt_target=} {rt_ratio=}"
    )
    if rt_count >= rt_target and ok_ratio:
        return True

def is_retweeted_by_categories_count(
        tweetdj: Tweetdj,
        category: List
    ):
    """Return dict if socialusers from listed categories retweeted status
    at least rt_target times
    tweetdj: Tweetdj object
    category: list of Categories objects
    """
    category_set = set(category.values_list("id", flat=True))
    rt_dict = {}
    for cat in category:
        rt_dict[cat.id] = {"name": cat.name, "count": 0}
        logger.debug(f"{rt_dict=}")
    for su in tweetdj.retweeted_by.all():
        su_category_set = set(su.category.values_list("id", flat=True))
        for pk in (su_category_set & category_set):
            rt_dict[pk]["count"] += 1
    logger.debug(f"{rt_dict=}")
    return rt_dict