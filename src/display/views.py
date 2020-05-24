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
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template

from timeline.models import last_retweeted_statusid_lst
from conversation.tree.tweet_parser import Tweet
from conversation.tree.tweet_server import get_tweet
from conversation.utils import top_statusid_lst, help_statusid_lst
from conversation.models import Treedj, Tweetdj
from moderation.tasks import handle_create_update_profile
from moderation.profile import is_profile_uptodate
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.translation import get_language_from_request
from django.utils.text import slugify
from django.template import Context, Template

from moderation.models import SocialUser, Category
from display.models import WebTweet, create_or_update_webtweet
from community.helpers import get_community
from display.tasks import  handle_scrape_status

from landing.templatetags.landing_tags import hashtag_lst


logger = logging.getLogger(__name__)

def get_display_cache():
    try:
        return settings.DISPLAY_CACHE
    except ImproperlyConfigured as e:
        return 60
        logger.error("DISPLAY_CACHE improperly configured in settings", e)

def cache_uid(title, request):
    """
    Unique identifier for cache
    """
    language = get_language_from_request(request)
    site = get_current_site(request)
    _cache_uid = f"{slugify(title)}_{language}_{site.id}"
    logger.debug(_cache_uid)
    return _cache_uid
    

class Status(TemplateView):
    title = _("Status")
    template_name = "display/display.html"
        
    def get_context_data(self, *args, **kwargs):
        context = super(Status, self).get_context_data(*args, **kwargs)
        logger.debug(f"statusid: {self.kwargs['statusid']}")
        statusid= self.kwargs['statusid']
        logger.debug(type(statusid))
        tweet = statuscontext(statusid)
        logger.debug(f"type: {type(tweet)}")
        logger.debug(f"type: {type(tweet)}")
        context['tweet_lst'] = [tweet]

        context['display_cache'] = get_display_cache()
        return context


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
        community = get_community(self.request)
        if not community:
            return context
        sid_lst = last_retweeted_statusid_lst(hourdelta=self.hour, community=community)[:self.n]
        tweet_lst = []
        logger.debug(f"id_list: {sid_lst}")
        for sid in sid_lst:
            logger.debug(f"type: {type(sid)}")
            tweet_lst.append(statuscontext(sid))
        context['tweet_lst'] = tweet_lst
        context['display_cache'] = get_display_cache()
        context['cache_uid'] = cache_uid(self.title,self.request)
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
        community = get_community(self.request)
        if not community:
            return context
        sid_lst = top_statusid_lst(self.hour, community)[:self.n]
        tweet_lst = []
        logger.debug(f"id_list: {sid_lst}")
        for sid in sid_lst:
            logger.debug(f"type: {type(sid)}")
            tweet_lst.append(statuscontext(sid))
        context['tweet_lst'] = tweet_lst
        context['display_cache'] = get_display_cache()
        context['cache_uid'] = cache_uid(self.title,self.request)
        return context
    
class Help(TemplateView):
    """
    Return a template view of the n last statuses in the user timeline of the
    authenticated account, excluding replies.
    """
    n = settings.STATUS_DISPLAY_NUMBER.get('help', 20)
    hour = settings.STATUS_DISPLAY_HOUR.get('help', 72)
    title = _("Help tweets")
    template_name = "display/display.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super(Help, self).get_context_data(*args, **kwargs)
        community = get_community(self.request)
        if not community:
            return context
        sid_lst = help_statusid_lst(self.hour, community)[:self.n]
        tweet_lst = []
        logger.debug(f"id_list: {sid_lst}")
        for sid in sid_lst:
            logger.debug(f"type: {type(sid)}")
            tweet_lst.append(statuscontext(sid))
        context['tweet_lst'] = tweet_lst
        context['display_cache'] = get_display_cache()
        context['cache_uid'] = cache_uid(self.title, self.request)
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
        context['display_cache'] = get_display_cache()
        context['cache_uid'] = cache_uid(self.title,self.request)
        community = get_community(self.request)
        if not community:
            return context
        logger.debug(f"community id: {community.id}, name: {community.name}")
        tweet_lst_dic = {}

        #last
        sid_lst = last_retweeted_statusid_lst(self.hour, community)[:self.n]
        last_tweet_lst = []
        logger.debug(f"id_list: {sid_lst}")
        for sid in sid_lst:
            last_tweet_lst.append(statuscontext(sid))
        for tweet in last_tweet_lst:
            logger.debug(f"last_tweet: {tweet.html}")
        tweet_lst_dic['last']= last_tweet_lst
        """
        #help
        sid_lst = help_statusid_lst(self.hour, community)[:self.n]
        help_tweet_lst = []
        #logger.debug(f"id_list: {sid_lst}")
        for sid in sid_lst:
            #logger.debug(f"type: {type(sid)}")
            help_tweet_lst.append(statuscontext(sid))
        tweet_lst_dic['help'] = help_tweet_lst
        
        #top
        sid_lst = top_statusid_lst(self.hour, community)[:self.n]
        top_tweet_lst = []
        #logger.debug(f"id_list: {sid_lst}")
        for sid in sid_lst:
            #logger.debug(f"type: {type(sid)}")
            top_tweet_lst.append(statuscontext(sid))
        tweet_lst_dic['top']=top_tweet_lst
        """
        # covid19
        sid_lst = tweetdj_tag(["covid19",])[:self.n]
        covid19_tweet_lst = []
        for sid in sid_lst:
            covid19_tweet_lst.append(statuscontext(sid))
        tweet_lst_dic['covid19']=covid19_tweet_lst
        
        context['display'] = tweet_lst_dic
        # get hashtag list into template variable hashtag_lst
        template = get_template('landing/hashtag_lst.html')
        cntxt = hashtag_lst(context)
        logger.debug(f"context: {cntxt}")
        context['hashtag_lst'] = template.render(cntxt)
        return context

def notfound(sid):
    msg = _("We couldn't find a tweet with id %s. "
           "This tweet might not be in our archive yet, or it was "
           "deleted, or the id is not correct. "
           "Sorry about that!" % sid)
    html = "<html><body>{} 🙇</body></html>".format(msg)
    tweet = Tweet(0)
    setattr(tweet, 'html', mark_safe(html))
    return tweet

def statuscontext(sid):
    try:
        tweet_mi = WebTweet.objects.get(statusid=sid)
    except WebTweet.DoesNotExist:
        handle_scrape_status.apply_async(args=(sid,))
        return notfound(sid)

    if not is_profile_uptodate(tweet_mi.userid):
        handle_create_update_profile.apply_async(args=(tweet_mi.userid,))

    logger.debug(f"tweet_mid: {tweet_mi}")
    localdatetime: str = time.strftime('%H:%M - %d %b %Y', tweet_mi.localtime())
    utcdatetime: str = time.strftime('%d %B %Y %H:%M:%S', tweet_mi.utctime())
    html = addurl(tweet_mi.html, "https://twitter.com")    
    setattr(tweet_mi, 'localdatetime', localdatetime)
    setattr(tweet_mi, 'utcdatetime', utcdatetime)
    setattr(tweet_mi, 'node', get_descendant_count(sid))
    setattr(tweet_mi, 'biggeravatar', get_biggeravatar_url(tweet_mi.userid))
    setattr(tweet_mi, 'normalavatar', get_normalavatar_url(tweet_mi.userid))
    tweet_mi.html = mark_safe(html)
    return tweet_mi

def get_biggeravatar_url(userid):
    try:
        return SocialUser.objects.get(user_id=userid).profile.biggeravatar.url
    except SocialUser.DoesNotExist:
        pass
    except ObjectDoesNotExist:
        pass
    else:
        return static("moderation/twitter_unknown_images/egg73x73.png")

def get_normalavatar_url(userid):
    try:
        return SocialUser.objects.get(user_id=userid).profile.normalavatar.url
    except SocialUser.DoesNotExist:
        pass
    except ObjectDoesNotExist:
        pass
    else:
        return static("moderation/twitter_unknown_images/egg48x48.png")       

def get_descendant_count(sid):
    try:
        return Treedj.objects.get(statusid=sid).get_descendant_count()
    except Treedj.DoesNotExist:
        return

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

def tweetdj_tag(tag_lst):
    """Return list of status id of statuses containing on of the tag in the list
    """
    category_names: List[str] = settings.COVID19_CATEGORIES
    category: List[Category] = []
    for category_name in category_names:
        try:
            _category = Category.objects.get(name=category_name)
            category.append(_category)
        except Category.DoesNotExist:
            continue
        
    return list(
            Tweetdj.objects
            .filter(socialuser__category__in=category)
            .filter(tags__name__in=tag_lst)
            .values_list('statusid', flat=True)
    )


class Covid19(TemplateView):
    """
    Return a template view of statuses with covid19 tag.
    """
    title = _("covid-19 tweets")
    template_name = "display/display.html"
    tag: List = ["covid19"]
    def get_context_data(self, *args, **kwargs):
        context = super(Covid19, self).get_context_data(*args, **kwargs)
        sid_lst = tweetdj_tag(self.tag)
        tweet_lst = []
        for sid in sid_lst:
            tweet_lst.append(statuscontext(sid))
        context['tweet_lst'] = tweet_lst
        context['display_cache'] = get_display_cache()
        context['cache_uid'] = cache_uid(self.title, self.request)
        return context