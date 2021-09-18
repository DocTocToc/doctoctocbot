import logging
import random
import time
import datetime
from moderation.social import update_social_ids
from messenger.models import Campaign, Receipt
from moderation.models import SocialUser, Follower
from crowdfunding.models import ProjectInvestment
from conversation.models import Tweetdj
from django.utils.formats import localize
from constance import config
from bot.tweepy_api import get_api
from tweepy import TweepError
from django.db.models import Q

logger = logging.getLogger(__name__)


def hoursago(hours):
    delta = datetime.timedelta(hours=hours)
    return datetime.datetime.now() - delta

def sleep_random(campaign):
    duration = randinterval(campaign)
    if not duration:
        return
    time.sleep(duration)

def randinterval(campaign):
    backoff = campaign.backoff
    if backoff <= 0:
        return
    variance = backoff*0.1
    return random.randint(
        int(round(backoff-variance)),
        int(round(backoff+variance))
    )

def _format(message, socialuser, campaign):
    d = {
        'screen_name' : socialuser.profile.screen_name_tag(),
    }
    return message.content.format(**d)

def run_campaign(campaign: Campaign):
    bot_su = campaign.account
    if not bot_su:
        logger.debug(f"No account set for campaign {campaign.name}, aborting.")
        return
    bot_screen_name = bot_su.screen_name_tag()
    update_social_ids(
        bot_su,
        cached=True,
        bot_screen_name=bot_screen_name,
        relationship="followers",    
    )
    recipient_qs = recipients(campaign)
    logger.debug(recipient_qs)
    ThroughModel = Campaign.recipients.through
    ThroughModel.objects.bulk_create(
        [ThroughModel(socialuser_id=su.id, campaign_id=campaign.id) for su in recipient_qs],
        ignore_conflicts=True
    )
    campaign.refresh_from_db()
    logger.debug(campaign.recipients.all())
    send(campaign)

def recipients(campaign: Campaign):
    bot_su = campaign.account
    bot_follower_id = Follower.objects.filter(user=bot_su).latest().id_list
    logger.debug(bot_follower_id)
    qs = SocialUser.objects.filter(user_id__in=bot_follower_id)
    if campaign.restrict_by_category is not None:
        qs = filter_category(qs, campaign)
    if campaign.restrict_by_crowdfunding is not None:
        qs = filter_crowdfunding(qs, campaign)
    if campaign.retweet_range:
        qs = filter_retweet_range(qs, campaign)
    return qs

def filter_category(qs, campaign):
    ids = []
    for category in campaign.categories.all():
        ids.extend(
            category.socialuser_set.values_list("id", flat=True)
        )
    # remove None items
    ids = list(filter(None, ids))
    if campaign.restrict_by_category:
        qs = qs.filter(id__in=ids)
    else:
        qs = qs.exclude(id__in=ids)
    return qs

def filter_crowdfunding(qs, campaign):
    ids = []
    for cc in campaign.crowdfunding_campaign.all():
        _su = ProjectInvestment.objects.filter(
            paid=True,
            datetime__gte=cc.start_datetime,
            datetime__lte=cc.end_datetime,
            project=cc.project
        ).values_list("user__socialuser__id", flat=True)
        ids.extend(
            list(_su)
        )
    # remove None items
    ids = list(filter(None, ids))
    if campaign.restrict_by_crowdfunding:
        logger.debug("filter")
        qs = qs.filter(id__in=ids)
    else:
        logger.debug("exclude")
        qs = qs.filter(~Q(id__in=ids))
    return qs

def filter_retweet_range(qs, campaign):
    range = campaign.retweet_range
    filtered_su_ids = []
    #su_ids = qs.values_list("id", flat=True)
    bot_su = campaign.account
    tweetdj_rt_by_bot_qs = Tweetdj.objects.filter(retweeted_by=bot_su)
    for su in qs:
        count = tweetdj_rt_by_bot_qs.filter(socialuser=su).count()
        if count in range:
            filtered_su_ids.append(su.id)
    qs = qs.filter(id__in=filtered_su_ids)
    return qs

def send(campaign: Campaign):
    username = campaign.account.screen_name_tag()
    if not username:
        return
    api = get_api(
        username=username,
        backend=True,
    )
    messages = campaign.messages.all()
    try:
        current_limit = config.messenger__campaign__dm_limit
    except AttributeError as e:
        logger.error("'messenger__campaign__dm_limit' not set", e)
        current_limit = 100
    for recipient in campaign.recipients.all():
        if current_limit == 0:
            return
        sleep_random(campaign)
        for msg in messages:
            text=_format(msg, recipient, campaign)
            receipts = Receipt.objects.filter(
                campaign = campaign,
                message = msg,
                user = recipient
            )
            skip=False
            if receipts:
                for r in receipts:
                    if r.event_id:
                        skip=True
                        break
            if skip:
                continue
            try:
                res = api.send_direct_message(
                    recipient_id=recipient.user_id,
                    text=text
                )
                logger.debug(res)
            except TweepError as e:
                logger.error(f"addstatus: Tweepy error: {e}")
                # code 150:
                # You cannot send messages to users who are not following you.
                # code 349
                # You cannot send messages to this user.
                # code 226:
                # This request looks like it might be automated. To protect our
                # users from spam and other malicious activity, we can't
                # complete this action right now. Please try again later.
                try:
                    error_code =  e.args[0][0]['code']
                    if error_code in [420, 429, 88, 226]:
                        logger.error(f"Twitter API error code: {error_code}")
                        current_limit=0
                except:
                    error_code = 0
            current_limit-=1
            r = Receipt(
                campaign=campaign,
                message=msg,
                user=recipient
            )
            try:
                r.event_id = res.id
                r.save()
            except:
                r.error = error_code
                r.save()