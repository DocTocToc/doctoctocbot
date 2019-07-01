from datetime import datetime
from django.conf import settings
from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models.functions import TruncMonth, TruncYear
from django.http import JsonResponse
from django.shortcuts import render
import logging
import time

from conversation.models import Tweetdj, Hashtag
from moderation.models import SocialUser


logger = logging.getLogger(__name__)

def filter_hashtag(qs):
    dct = dict()
    for h in Hashtag.objects.all():
        dct[h.hashtag]= h
    h = settings.KEYWORD_TRACK_LIST
    h0_OR_h1 = qs.filter(Q(hashtag=dct[h[0]]) | Q(hashtag=dct[h[1]]))
    h0_AND_h1 =   qs.filter(hashtag=dct[h[0]]).filter(hashtag=dct[h[1]])
    h0 = qs.filter(hashtag=dct[h[0]])
    h1 = qs.filter(hashtag=dct[h[1]])
    
    return [h0_OR_h1, h0_AND_h1, h0, h1]    

def daily(request):
    return render(request, 'charts/daily.html')

def questions_daily_data(request):
    if request.user.is_authenticated:
        user = request.user
        logger.debug(user.username)
        if user.socialuser is not None:
            logger.debug(user.socialuser.user_id)
    else:
        logger.debug("No authenticated user.")
    
    physicians = SocialUser.objects.physician_users()
    #logger.debug(physicians)
    qsd = (Tweetdj.objects
        .filter(userid__in=physicians)
        .filter(retweetedstatus=False)
        .filter(quotedstatus=False)
        .extra({'date' : "date(created_at)"})
        .values('date')
        .annotate(count=Count('statusid')))
    
    series_lst = []
    qs_lst = filter_hashtag(qsd)
    
    if request.user.is_authenticated and request.user.socialuser is not None:
        qs_user_lst = []
        uid = request.user.socialuser.user_id
        for qs in qs_lst:
            qs = qs.filter(userid=uid)
            qs_user_lst.append(qs)
        qs_lst.extend(qs_user_lst)
        
    for qs in qs_lst:
        series = []
        for data in qs:
            d = data["date"]
            timestamp = time.mktime(d.timetuple())*1000
            count = data["count"]
            plot = [timestamp, count]
            series.append(plot)
        series_lst.append(series)
        
    #logger.debug(series)

    chart = {
        'chart': {'type': 'column'},
        'title': {'text': 'Number of questions per day'},
        'xAxis': {'type': 'datetime' },
        'yAxis': {'title': {'text': 'Number of tweets'}},
        'series': [
                {
                'name': 'Dayly tweets #DocTocToc or #DocsTocToc',
                'data': series_lst[0],
                'color': 'rgba(51, 133, 55)'
                },
                                {
                'name': 'Dayly tweets #DocTocToc and #DocsTocToc',
                'data': series_lst[1],
                'color': 'rgba(192, 192, 192)'
                },
                                                {
                'name': 'Daily tweets #DocTocToc',
                'data': series_lst[2],
                'color': 'rgba(0, 0, 255)'
                },
                {
                'name': 'Daily tweets #DocsTocToc',
                'data': series_lst[3],
                'color': 'rgba(255, 0, 0)'
                }
        ]
    }
    if len(series_lst)==6:
        dict3 = {'name': 'Your daily #DocTocToc tweets', 'data': series_lst[3]}
        dict4 = {'name': 'Your daily #DocsTocToc tweets', 'data': series_lst[4]}
        dict5 = {'name': 'Your daily #DocsTocToc and/or #DocsTocToc tweets', 'data': series_lst[5]}
        chart['series'].extend([dict3, dict4, dict5])
        
    return JsonResponse(chart)

def monthly(request):
    return render(request, 'charts/monthly.html')

def questions_monthly_data(request):
    physicians = SocialUser.objects.physician_users()
    '''
    qsm0or1 = Tweetdj.objects \
        .filter(userid__in=physicians) \
        .annotate(year = ExtractYear('created_at'), month = ExtractMonth('created_at')) \
        .values('year', 'month') \
        .annotate(count=Count('statusid')) \
        .values('year', 'month', 'count') \
        .order_by('year', 'month')
    '''    
    qsm = (Tweetdj.objects
        .filter(userid__in=physicians)
        .filter(retweetedstatus=False)
        .filter(quotedstatus=False)
        .annotate(date = TruncMonth('created_at'))
        .values('date')
        .annotate(count=Count('statusid'))
        .order_by('date'))
    
    qs_lst = filter_hashtag(qsm)
    
    series_lst = []
    for qs in qs_lst:
        series = []
        for data in qs:
            d = data["date"]
            timestamp = time.mktime(d.timetuple())*1000
            count = data["count"]
            plot = [timestamp, count]
            series.append(plot)
        series_lst.append(series)
    
    chart = {
        'chart': {'type': 'column'},
        'title': {'text': 'Number of tweets per month (verified physicians only)'},
        'xAxis': {'type': 'datetime'},
        'yAxis': {'title': {'text': 'Number of tweets'}},
        'series': [
                {
                'name': 'Monthly tweets #DocTocToc or #DocsTocToc',
                'data': series_lst[0],
                'color': 'rgba(51, 133, 55)'
                },
                                {
                'name': 'Monthly tweets #DocTocToc and #DocsTocToc',
                'data': series_lst[1],
                'color': 'rgba(192, 192, 192)'
                },
                                                {
                'name': 'Monthly tweets #DocTocToc',
                'data': series_lst[2],
                'color': 'rgba(0, 0, 255)'
                },
                {
                'name': 'Monthly tweets #DocsTocToc',
                'data': series_lst[3],
                'color': 'rgba(255, 0, 0)'
                }
            ]
        }
    return JsonResponse(chart)

def questions_yearly_data(request):
    physicians = SocialUser.objects.physician_users()
    '''
    qsm0or1 = Tweetdj.objects \
        .filter(userid__in=physicians) \
        .annotate(year = ExtractYear('created_at'), month = ExtractMonth('created_at')) \
        .values('year', 'month') \
        .annotate(count=Count('statusid')) \
        .values('year', 'month', 'count') \
        .order_by('year', 'month')
    '''    
    qsy = (Tweetdj.objects
        .filter(userid__in=physicians)
        .filter(retweetedstatus=False)
        .filter(quotedstatus=False)
        .annotate(date = TruncYear('created_at'))
        .values('date')
        .annotate(count=Count('statusid'))
        .order_by('date'))
    
    qs_lst = filter_hashtag(qsy)

    series_lst = []
    for qs in qs_lst:
        series = []
        for data in qs:
            d = data["date"]
            timestamp = time.mktime(d.timetuple())*1000
            count = data["count"]
            plot = [timestamp, count]
            series.append(plot)
        series_lst.append(series)
    
    chart = {
        'chart': {'type': 'column'},
        'title': {'text': 'Number of tweets per year (verified physicians only)'},
        'xAxis': {'type': 'datetime'},
        'yAxis': {'title': {'text': 'Number of tweets'}},
        'series': [
                {
                'name': 'Yearly tweets #DocTocToc or #DocsTocToc',
                'data': series_lst[0],
                'color': 'rgba(51, 133, 55)'
                },
                                {
                'name': 'Yearly tweets #DocTocToc and #DocsTocToc',
                'data': series_lst[1],
                'color': 'rgba(192, 192, 192)'
                },
                                                {
                'name': 'Yearly tweets #DocTocToc',
                'data': series_lst[2],
                'color': 'rgba(0, 0, 255)'
                },
                {
                'name': 'Yearly tweets #DocsTocToc',
                'data': series_lst[3],
                'color': 'rgba(255, 0, 0)'
                }
            ]
        }
    return JsonResponse(chart)

def yearly(request):
    return render(request, 'charts/yearly.html')