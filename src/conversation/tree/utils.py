from datetime import datetime
from typing import Optional, List, Set
import logging

from django.db.utils import DatabaseError
from django.core.cache import cache
from constance import config

from conversation.models import Tweetdj, Treedj
from community.models import Community
from community.helpers import (
    get_community_bot_socialuser,
)
from community.helpers import get_community_member_id

logger = logging.getLogger(__name__)

def get_community_roots(
        community: Community,
        lower_dt: Optional[datetime] = None,
        upper_dt: Optional[datetime] = None,
    ):    
    su = get_community_bot_socialuser(community)
    if not su:
        return
    rt_by_qs = Tweetdj.objects.filter(
        retweeted_by=su,
        json__in_reply_to_status_id=None
    )
    if lower_dt or upper_dt:
        rt_by_qs = limit_by_dt(
            rt_by_qs,
            lower_dt,
            upper_dt
        )
    rt_by_ids = rt_by_qs.values_list("statusid", flat=True)
    roots = list(
        Treedj.objects
        .filter(statusid__in=[rt_by_ids])
        .order_by("-statusid")
        .values_list("statusid", flat=True)
    )
    return roots

def limit_by_dt(
        qs,
        lower_dt: Optional[datetime] = None,
        upper_dt: Optional[datetime] = None,
    ):
    if lower_dt and upper_dt:
        return qs.filter(created_at__gte=lower_dt, created_at__lte=upper_dt)
    elif lower_dt:
        return qs.filter(created_at__gte=lower_dt)
    elif upper_dt:
        return qs.filter(created_at__lte=upper_dt)
    else:
        return qs

def add_leaf(parent_id, statusid):
    try:
        parent = Treedj.objects.get(statusid=parent_id)
    except Treedj.DoesNotExist:
        return
    try:
        Treedj.objects.create(
            statusid=statusid,
            parent=parent
        )
    except DatabaseError:
        return

def add_tweetdj_to_treedj():
    # create a set of all treedj pk
    tree_sid: Set[int] = set(
        Treedj.objects.values_list("statusid", flat=True)
    )
    # loop over all tweetdj and check if the parent tweet is in the treedj set
    for _dct in (
        Tweetdj.objects
        .filter(parentid__isnull=False)
        .order_by('statusid')
        .values("statusid", "parentid")
    ):
    #parent_id = tweetdj.json["in_reply_to_status_id"]
        if _dct["parentid"] in tree_sid and _dct["statusid"] not in tree_sid:
            add_leaf(_dct["parentid"], _dct["statusid"])

def reply_by_member_count(statusid: int, community: Community) ->Optional[int]:
    """
    Return the number of replies by members of the community
    (except the author)
    """
    if not statusid or not isinstance(community, Community):
        return
    cache_ttl = (
        config.conversation__tree__utils__reply_by_member_count__cache_ttl
    )
    cache_name = f"reply_by_member_count_{community.name}_{statusid}"
    count = cache.get(cache_name)
    if not count:
        try:
            root = Treedj.objects.get(statusid=statusid)
        except Treedj.DoesNotExist as e:
            logger.debug(f"{e}")
            return
        try:
            root_tweetdj = Tweetdj.objects.get(statusid=statusid)
            root_user_id = root_tweetdj.userid
        except Tweetdj.DoesNotExist as e:
            logger.debug(f"{e}")
            return
        leaves = root.get_descendants(include_self=False)
        if not leaves:
            count = 0
            cache.set(cache_name, count, cache_ttl)
            return count
        leaves_statusid = leaves.values_list("statusid", flat=True)
        count = (
            Tweetdj.objects
            .filter(statusid__in=leaves_statusid)
            .filter(userid__in=get_community_member_id(community))
            .exclude(userid=root_user_id)
            .count()
        )
        cache.set(cache_name, count, cache_ttl)
    return count


class StatusTree(object):
    def __init__(self, statusid):
        try:
            node = Treedj.objects.get(statusid=statusid)
        except Treedj.DoesNotExist as e:
            logger.error(f"Cannot create StatusTree because {e}")
            return
        root = node.get_root()
        self.root = root

    def root_user_nodes(self):
        """Return QuerySet of nodes of the tree created by the creator of the
        root status
        :returns: QuerySet of all the Treedj nodes created by the creator of
        the root node
        :rtype: QuerySet
        """
        all_nodes =  self.root.get_descendants(include_self=True)
        try:
            root_userid = Tweetdj.objects.get(statusid=self.root.statusid).userid
        except Tweetdj.DoesNotExist:
            return
        root_user_statusids = Tweetdj.objects \
            .filter(statusid__in=all_nodes.values_list("statusid", flat=True)) \
            .filter(userid=root_userid) \
            .values_list("statusid", flat=True)
        return all_nodes.filter(statusid__in=root_user_statusids)