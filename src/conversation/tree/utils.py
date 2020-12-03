from datetime import datetime
from typing import Optional
from conversation.models import Tweetdj, Treedj
from community.models import Community
from community.helpers import (
    get_community_bot_socialuser,
)

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