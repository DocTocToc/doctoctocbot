from datetime import datetime
import logging
import time

from django.utils import translation
from django.conf import settings
from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models.functions import TruncMonth, TruncYear
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy, ngettext_lazy
from django.utils.text import format_lazy

from conversation.models import Tweetdj, Hashtag
from moderation.models import SocialUser, UserCategoryRelationship
from community.helpers import get_community
from moderation.profile import screen_name

logger = logging.getLogger(__name__)

color_dct = {
    "h0": "rgba(0, 0, 128)", #Navy
    "h1": "rgba(230, 25, 75)", #Red
    "or": "rgba(145, 30, 180)", #Purple
    "and": "rgba(60, 180, 75)", #Green
    "h0_user": "rgba(0, 130, 200)", #Blue
    "h1_user": "rgba(250, 190, 190)", #Pink
    "or_user": "rgba(230, 190, 255)", #Lavender
    "and_user": "rgba(170, 255, 195)", #Mint
}

by = gettext_lazy("by")

def authenticated_socialuser_userid(request):
    if request.user.is_authenticated:
        if request.user.socialuser is not None:
            return request.user.socialuser.user_id

def get_userid_lst(request):
    community = get_community(request)
    categories = community.membership.all()
    return UserCategoryRelationship.objects.filter(
        category__in = categories,
        community = community
        ).values_list('social_user__user_id', flat=True)

def get_chart(period, request, series):
    """
    Get HighCharts json chart corresponding to given attributes
    """
    with translation.override('en'):
        period_en = str(period)
        logger.debug(f"period_en: {period_en}")
    categories = get_community(request).membership.all()
    categories_str = ", ".join([cat.label for cat in categories])
    return {
        'chart': {'type': 'column'}, 
        'title': {'text': _('Number of questions per {period} ({categories_str})').format(
            period=period,
            categories_str=categories_str)
        },
        'xAxis': {
            'type': 'datetime',
#            'minTickInterval': moment.duration(1, 'month').asMiliseconds()
        },
        'yAxis': {
            'title': {'text': _('Number of tweets')},
            'allowDecimals': False,
        },
        'series': series
    }

def filter_hashtag(qs, request):
    """
    Filter tweets by presence of community's hashtag(s).
    """
    community = get_community(request)
    h_lst = community.hashtag.all()
    logger.debug(f"all hahstags: {h_lst}")
    if not h_lst:
        return
    if len(h_lst)==1:
        h0_label = h_lst[0].hashtag
        return {
            "h0": {
                "label": h0_label,
                "qs": qs.filter(hashtag__hashtag = h0_label)
            }
        }
    elif len(h_lst)>1:
        or_txt = gettext_lazy("or")
        and_txt = gettext_lazy("and")
        h1_label = h_lst[1].hashtag
        h0_label = h_lst[0].hashtag
        return {
            "h0": {
                "label": h0_label,
                "qs": qs.filter(hashtag__hashtag = h0_label)
            },
            "h1": {
                "label": h1_label,
                "qs": qs.filter(hashtag__hashtag = h1_label)
            },
            "or": {
                "label": format_lazy('{h0} {or_txt} {h1}',
                                     h0=h0_label,
                                     or_txt=or_txt,
                                     h1=h1_label),
                "qs": qs.filter(Q(hashtag=h_lst[0]) | Q(hashtag=h_lst[1]))
            },
            "and": {
                "label": format_lazy('{h0} {and_txt} {h1}',
                                     h0=h0_label,
                                     and_txt=and_txt,
                                     h1=h1_label),
                "qs": qs.filter(hashtag=h_lst[0]).filter(hashtag=h_lst[1])
            }
        }

def daily(request):
    return render(request, 'charts/daily.html')

def questions_daily_data(request):
    period = gettext_lazy("day")
    member_userid_lst = get_userid_lst(request)        

    qsd = (Tweetdj.objects
        .filter(userid__in=member_userid_lst)
        .filter(retweetedstatus=False)
        .filter(quotedstatus=False)
        .extra({'date' : "date(created_at)"})
        .values('date')
        .annotate(count=Count('statusid')))

    qs_dct = filter_hashtag(qsd, request) # qs_dct was 'qs_lst'
    
    uid = authenticated_socialuser_userid(request)
    qs_dct_copy = dict(qs_dct)
    if uid:
        for key in qs_dct_copy.keys():
            qs_dct.update(
                {f"{key}_user": {
                    "label": f'{qs_dct_copy[key]["label"]} {by} {screen_name(uid)}',
                    "qs": qs_dct_copy[key]["qs"].filter(userid=uid)
                    }
                }
            )

    series = list()
    for key, dct in qs_dct.items():
        serie = dict()
        serie.update({"name": f'{dct["label"]}'})
        serie.update({"color": color_dct[key]})                      
        data = []
        for values in dct["qs"]:
            d = values["date"]
            timestamp = int(time.mktime(d.timetuple())*1000)
            count = values["count"]
            data.append([timestamp, count])
        serie.update({"data": data})
        series.append(serie)
    chart = get_chart(period, request, series)
    return JsonResponse(chart)

def monthly(request):
    return render(request, 'charts/monthly.html')

def questions_monthly_data(request):
    period = gettext_lazy("month")
    member_userid_lst = get_userid_lst(request)        
 
    qsm = (Tweetdj.objects
        .filter(userid__in=member_userid_lst)
        .filter(retweetedstatus=False)
        .filter(quotedstatus=False)
        .annotate(date = TruncMonth('created_at'))
        .values('date')
        .annotate(count=Count('statusid'))
        .order_by('date'))
    
    qs_dct = filter_hashtag(qsm, request)
    
    uid = authenticated_socialuser_userid(request)
    qs_dct_copy = dict(qs_dct)
    if uid:
        for key in qs_dct_copy.keys():
            qs_dct.update(
                {f"{key}_user": {
                    "label": f'{qs_dct_copy[key]["label"]} {by} {screen_name(uid)}',
                    "qs": qs_dct_copy[key]["qs"].filter(userid=uid)
                    }
                }
            )
    
    series = list()
    for key, dct in qs_dct.items():
        serie = dict()
        serie.update({"name": f'{dct["label"]}'})
        serie.update({"color": color_dct[key]})                      
        data = []
        for values in dct["qs"]:
            d = values["date"]
            timestamp = int(time.mktime(d.timetuple())*1000)
            count = values["count"]
            data.append([timestamp, count])
        serie.update({"data": data})
        series.append(serie)
    chart = get_chart(period, request, series)
    return JsonResponse(chart)

def yearly(request):
    return render(request, 'charts/yearly.html')

def questions_yearly_data(request):
    period = gettext_lazy("year")
    member_userid_lst = get_userid_lst(request)        
    
    qsy = (Tweetdj.objects
        .filter(userid__in=member_userid_lst)
        .filter(retweetedstatus=False)
        .filter(quotedstatus=False)
        .annotate(date = TruncYear('created_at'))
        .values('date')
        .annotate(count=Count('statusid'))
        .order_by('date'))
    
    qs_dct = filter_hashtag(qsy, request)

    uid = authenticated_socialuser_userid(request)
    qs_dct_copy = dict(qs_dct)
    if uid:
        for key in qs_dct_copy.keys():
            qs_dct.update(
                {f"{key}_user": {
                    "label": f'{qs_dct_copy[key]["label"]} {by} {screen_name(uid)}',
                    "qs": qs_dct_copy[key]["qs"].filter(userid=uid)
                    }
                }
            )
    series = list()
    for key, dct in qs_dct.items():
        serie = dict()
        serie.update({"name": f'{dct["label"]}'})
        serie.update({"color": color_dct[key]})                      
        data = []
        for values in dct["qs"]:
            d = values["date"]
            timestamp = int(time.mktime(d.timetuple())*1000)
            count = values["count"]
            data.append([timestamp, count])
        serie.update({"data": data})
        series.append(serie)
    chart = get_chart(period, request, series)
    return JsonResponse(chart)