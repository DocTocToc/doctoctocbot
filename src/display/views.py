import logging
import time

from typing import List
from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.conf import settings

from bot.bin.timeline import get_timeline_id_lst
from conversation.tree.tweet_parser import Tweet
from conversation.tree.tweet_server import get_tweet
from conversation.utils import top_statusid_lst, help_statusid_lst, last_authorized_statusid_lst

from .constants import DISPLAY_CACHE
from .models import WebTweet, create_or_update_webtweet


logger = logging.getLogger(__name__)


# Create your views here.
class Status(TemplateView):
    title = _("Status")
    template_name = "display/display.html"
        
    def get_context_data(self, *args, **kwargs):
        context = super(Status, self).get_context_data(*args, **kwargs)
        logger.debug(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! {self.kwargs['statusid']}")
        statusid= self.kwargs['statusid']
        logger.debug(type(statusid))
        tweet = statuscontext(statusid)
        logger.debug(f"type: {type(tweet)}")
        logger.debug(f"type: {type(tweet)}")
        context['tweet_lst'] = [tweet]
        context['display_cache'] = DISPLAY_CACHE
        return context
        #return render(request, 'display/display.html', context)

class Last(TemplateView):
    """
    Return a template view of the n last statuses in the user timeline of the
    authenticated account, excluding replies.
    """
    n = settings.STATUS_DISPLAY_NUMBER.get('last', 10)
    hour = settings.STATUS_DISPLAY_HOUR.get('last', 48)
    title = _("Last tweets")
    template_name = "display/display.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super(Last, self).get_context_data(*args, **kwargs)
        sid_lst = last_authorized_statusid_lst(self.hour)[:self.n]
        tweet_lst = []
        logger.debug(f"id_list: {sid_lst}")
        for sid in sid_lst:
            logger.debug(f"type: {type(sid)}")
            tweet_lst.append(statuscontext(sid))
        context['tweet_lst'] = tweet_lst
        context['display_cache'] = DISPLAY_CACHE
        return context
    
class Top(TemplateView):
    """
    Return a template view of the n last statuses in the user timeline of the
    authenticated account, excluding replies.
    """
    n = settings.STATUS_DISPLAY_NUMBER.get('top', 10)
    hour = settings.STATUS_DISPLAY_HOUR.get('top', 48)
    title = _("Top tweets")
    template_name = "display/display.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super(Top, self).get_context_data(*args, **kwargs)
        sid_lst = top_statusid_lst(self.hour)[:self.n]
        tweet_lst = []
        logger.debug(f"id_list: {sid_lst}")
        for sid in sid_lst:
            logger.debug(f"type: {type(sid)}")
            tweet_lst.append(statuscontext(sid))
        context['tweet_lst'] = tweet_lst
        context['display_cache'] = DISPLAY_CACHE
        return context
    
class Help(TemplateView):
    """
    Return a template view of the n last statuses in the user timeline of the
    authenticated account, excluding replies.
    """
    n = settings.STATUS_DISPLAY_NUMBER.get('help', 10)
    hour = settings.STATUS_DISPLAY_HOUR.get('help', 48)
    title = _("Help tweets")
    template_name = "display/display.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super(Help, self).get_context_data(*args, **kwargs)
        sid_lst = help_statusid_lst(self.hour)[:self.n]
        tweet_lst = []
        logger.debug(f"id_list: {sid_lst}")
        for sid in sid_lst:
            logger.debug(f"type: {type(sid)}")
            tweet_lst.append(statuscontext(sid))
        context['tweet_lst'] = tweet_lst
        context['display_cache'] = DISPLAY_CACHE
        return context

class All(TemplateView):
    """
    Return a template view of the n last statuses in the user timeline of the
    authenticated account, excluding replies.
    """
    n = settings.STATUS_DISPLAY_NUMBER.get('all', 10)
    hour = settings.STATUS_DISPLAY_HOUR.get('all', 48)
    title = _("All tweets")
    template_name = "display/all.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super(All, self).get_context_data(*args, **kwargs)
        
        tweet_lst_dic = {}
        
        #last
        sid_lst = last_authorized_statusid_lst(self.hour)[:self.n]
        last_tweet_lst = []
        logger.debug(f"id_list: {sid_lst}")
        for sid in sid_lst:
            last_tweet_lst.append(statuscontext(sid))
        for tweet in last_tweet_lst:
            logger.debug(f"last_tweet: {tweet.html}")
        tweet_lst_dic['last']= last_tweet_lst
        
        #help
        sid_lst = help_statusid_lst(self.hour)[:self.n]
        help_tweet_lst = []
        #logger.debug(f"id_list: {sid_lst}")
        for sid in sid_lst:
            #logger.debug(f"type: {type(sid)}")
            help_tweet_lst.append(statuscontext(sid))
        tweet_lst_dic['help'] = help_tweet_lst
        
        #top
        sid_lst = top_statusid_lst(self.hour)[:self.n]
        top_tweet_lst = []
        #logger.debug(f"id_list: {sid_lst}")
        for sid in sid_lst:
            #logger.debug(f"type: {type(sid)}")
            top_tweet_lst.append(statuscontext(sid))
        tweet_lst_dic['top']=top_tweet_lst
        
        context['display'] = tweet_lst_dic
        context['display_cache'] = DISPLAY_CACHE  
        return context

def notfound(sid):
    html = ("<html><body>We couldn't find a tweet with id %s. "
                        "This tweet was deleted or the id is not correct. "
                        "Sorry about that! 🙇"
                        "</body></html>" % sid)
    tweet = Tweet(0)
    setattr(tweet, 'html', mark_safe(html))
    return tweet

def statuscontext(sid):
    try:
        tweet_mi = WebTweet.objects.get(statusid=sid)
    except WebTweet.DoesNotExist:
        return notfound(sid)
    logger.debug(f"tweet_mid: {tweet_mi}")
    localdatetime: str = time.strftime('%H:%M - %d %b %Y', tweet_mi.localtime())
    utcdatetime: str = time.strftime('%d %B %Y %H:%M:%S', tweet_mi.utctime())
    html = addurl(tweet_mi.html, "https://twitter.com")    
    setattr(tweet_mi, 'localdatetime', localdatetime)
    setattr(tweet_mi, 'utcdatetime', utcdatetime)
    #tweet_mi.html = html
    tweet_mi.html = mark_safe(html)
    return tweet_mi

def addurl(fragment: str, url: str) -> str:
    logger.debug(f"fragment:{fragment}")
    if fragment is None:
        return
    def rawsoup(soup):
        if soup.body:
            return soup.body.next
        elif soup.html:
            return soup.html.next
        else:
            return soup

    soup = BeautifulSoup(fragment, 'lxml')
    logger.debug(f"soup before:{soup}")

    for a in soup.findAll('a', href=True):
        if a['href'].startswith('/'):
            a['href'] = url + a['href']
    logger.debug(f"soup after:{soup}")
    soup.html.unwrap()
    soup.body.unwrap()
    logger.debug(f"rawsoup:{str(soup)}")
    return str(soup)