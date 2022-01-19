import logging
import datetime
import markdown

from django import template
from django.utils.safestring import mark_safe
from django.template import Template
from django.core.cache import cache
from django.utils.formats import date_format
from django.utils import translation

from constance import config

from conversation.models import Tweetdj
from community.models import Retweet, ApiAccess, AccessLevel
from community.helpers import get_community, activate_language
from community.helpers import get_community_member_id
from bot.lib.snowflake import snowflake2utc


logger = logging.getLogger(__name__)

register = template.Library()



@register.simple_tag(takes_context=True)
def community_question_count(context):
    community = get_community(context['request'])
    if not community:
        return
    cache_ttl = (
        config.landing__community_question_count__cache_ttl
    )
    cache_name = f"community_question_count_{community.name}"
    count = cache.get(cache_name)
    if not count:
        # determine the hashtags that get retweeted among all the community's
        # hashtags
        h_id: List[int] = Retweet.objects \
                      .filter(community=community) \
                      .values_list('hashtag', flat=True) \
                      .distinct()
        count = Tweetdj.objects \
                       .filter(hashtag__id__in=h_id) \
                       .filter(userid__in=get_community_member_id(community)) \
                       .count()
        cache.set(cache_name, count, cache_ttl)
    return count

@register.simple_tag(takes_context=True)
def community_first_question_date(context):
    community = get_community(context['request'])
    if not community:
        return
    cache_ttl = (
        config.landing__community_first_question_date__cache_ttl
    )
    cache_name = f"community_first_question_date_{community.name}"
    date = cache.get(cache_name)
    if not date:
        # determine the hashtags that get retweeted among all the community's
        # hashtags
        h_id: List[int] = Retweet.objects \
                      .filter(community=community) \
                      .values_list('hashtag', flat=True) \
                      .distinct()
        first = Tweetdj.objects \
                       .filter(hashtag__id__in=h_id) \
                       .filter(userid__in=get_community_member_id(community)) \
                       .order_by("statusid") \
                       .first()
        if not first:
            return
        date = datetime.datetime.fromtimestamp(
            snowflake2utc(first.statusid)
        )
        language = translation.get_language_from_request(context.request)
        translation.activate(language)
        date = date_format(date, format='SHORT_DATE_FORMAT', use_l10n=True)
        cache.set(cache_name, date, cache_ttl)
    return date

@register.simple_tag(takes_context=True)
def api_access_status_limit(context):
    """Return the maximum number of statuses an anonymous user can access
    """
    community = get_community(context['request'])
    if not community:
        return
    try:
        access_level = AccessLevel.objects.get(name="anonymous")
    except AccessLevel.DoesNotExist as e:
        logger.error("anonymous access level does not exist {e}")
        return
    try:
        status_limit = ApiAccess.objects.get(
            community=community,
            level=access_level
        ).status_limit
    except ApiAccess.DoesNotExist:
        return
    return status_limit