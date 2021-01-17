from datetime import datetime
from typing import Optional, List, Set
from conversation.models import Tweetdj, Treedj
from community.models import Community
from community.helpers import (
    get_community_bot_socialuser,
)
from django.db.utils import DatabaseError

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
    for tweetdj in Tweetdj.objects.all():
        parent_id = tweetdj.parentid
        #parent_id = tweetdj.json["in_reply_to_status_id"]
        if parent_id in tree_sid and tweetdj.statusid not in tree_sid:
            add_leaf(parent_id, tweetdj.statusid)
                    