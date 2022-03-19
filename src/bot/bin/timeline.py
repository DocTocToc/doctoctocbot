from typing import List

from community.models import Community
from bot.tweepy_api import get_api
from bot.lib.statusdb import Addstatus
from bot.models import Account
from timeline.models import add_status_tl, Status
import tweepy
import logging
from conversation.timeline import get_user_timeline
from community.helpers import get_community_twitter_tweepy_api

logger = logging.getLogger(__name__)

def record_timeline():
    """Record bot timeline of active communities
    """
    for community in Community.objects.filter(active=True):
        account = community.account
        if not account:
            continue
        if not account.active:
            continue
        su = account.socialuser
        if not su:
            continue
        api = get_community_twitter_tweepy_api(community)
        if not api:
            continue
        get_user_timeline(
            userid=su.user_id,
            api=api,
            force=False
        )

def record_socialuser_timeline(socialuser):
    """Record timeline for SocialUser. (Limited to accounts for now.)"""
    # TODO: extend to all SocialUsers. If protected, check if it is the friend
    # of one of the accounts. 
    if socialuser.id in Account.objects.values_list("socialuser", flat=True):
        api = get_api(username=socialuser.screen_name_tag())
        get_user_timeline(
            userid=socialuser.user_id,
            api=api,
            force=False
        )