from datetime import datetime
import time
import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models.functions import TruncMonth, TruncYear

from conversation.models import Tweetdj
from moderation.models import SocialUser

logger = logging.getLogger(__name__)

def daily(request):
    return render(request, 'daily.html')

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
    qsd0or1 = Tweetdj.objects \
        .filter(userid__in=physicians) \
        .filter(retweetedstatus=False) \
        .filter(quotedstatus=False) \
        .extra({'date' : "date(created_at)"}) \
        .values('date') \
        .annotate(count=Count('statusid'))    
    qsd0 = qsd0or1.filter(hashtag0=True)
    qsd1 = qsd0or1.filter(hashtag1=True)
    
    series_lst = []
    qs_lst = [qsd0, qsd1, qsd0or1]
    
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
            'name': 'Daily questions hashtag0 DocTocToc',
            'data': series_lst[0],
            },
            {
            'name': 'Daily questions hashtag1 DocsTocToc',
            'data': series_lst[1],
            },
            {
            'name': 'Daily questions hashtag0 DocTocToc and/or hashtag1 DocsTocToc',
            'data': series_lst[2],
            },
            
        ]
    }
    if len(series_lst)==6:
        dict3 = {'name': 'Your daily #DocTocToc tweets', 'data': series_lst[3]}
        dict4 = {'name': 'Your daily #DocsTocToc tweets', 'data': series_lst[4]}
        dict5 = {'name': 'Your daily #DocsTocToc and/or #DocsTocToc tweets', 'data': series_lst[5]}
        chart['series'].extend([dict3, dict4, dict5])
        
    return JsonResponse(chart)

def monthly(request):
    return render(request, 'monthly.html')

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
    qsm0or1 = Tweetdj.objects \
        .filter(userid__in=physicians) \
        .annotate(date = TruncMonth('created_at')) \
        .values('date') \
        .annotate(count=Count('statusid')) \
        .order_by('date')
        
    qsm0 = qsm0or1.filter(hashtag0=True)
    qsm1 = qsm0or1.filter(hashtag1=True)
    
    qs_lst = [qsm0, qsm1, qsm0or1]
    
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
                'name': 'Monthly tweets #DocTocToc',
                'data': series_lst[0],
                'color': 'rgba(51, 133, 255)'
                },
                                {
                'name': 'Monthly tweets #DocsTocToc',
                'data': series_lst[1],
                'color': 'rgba(255, 77, 77)'
                },
                                                {
                'name': 'Monthly tweets #DocTocToc and/or #DocsTocToc',
                'data': series_lst[2],
                'color': 'rgba(105, 105, 105)'
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
    qsm0or1 = Tweetdj.objects \
        .filter(userid__in=physicians) \
        .annotate(date = TruncYear('created_at')) \
        .values('date') \
        .annotate(count=Count('statusid')) \
        .order_by('date')
        
    qsm0 = qsm0or1.filter(hashtag0=True)
    qsm1 = qsm0or1.filter(hashtag1=True)
    
    qs_lst = [qsm0, qsm1, qsm0or1]
    
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
                'name': 'Yearly tweets #DocTocToc',
                'data': series_lst[0],
                'color': 'rgba(51, 133, 255)'
                },
                                {
                'name': 'Yearly tweets #DocsTocToc',
                'data': series_lst[1],
                'color': 'rgba(255, 77, 77)'
                },
                                                {
                'name': 'Yearly tweets #DocTocToc and/or #DocsTocToc',
                'data': series_lst[2],
                'color': 'rgba(105, 105, 105)'
                }
            ]
        }
    return JsonResponse(chart)

def yearly(request):
    return render(request, 'yearly.html')