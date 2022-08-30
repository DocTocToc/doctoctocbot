import logging
import random
import time
import datetime
import re

from constance import config
from tweepy import TweepError

from django.db.models import Q
from django.utils.formats import date_format
from django.utils import timezone

from dm.models import DirectMessage
from bot.tweepy_api import get_api
from moderation.social import update_social_ids
from messenger.models import (
    Campaign,
    Receipt,
    Message,
    StatusLog,
    MessengerCrowdfunding,
)
from moderation.models import SocialUser, Follower, Profile
from crowdfunding.models import ProjectInvestment, Project
from conversation.models import Tweetdj
from moderation.profile import recent_twitter_screen_name
from community.helpers import site_url, activate_language
from django.template.defaultfilters import date as _date
from moderation.profile import create_update_profile_twitter

logger = logging.getLogger(__name__)


class CampaignManager:
    def __init__(
            self,
            campaign: Campaign,
            dry_run: bool = False,
            cache_followers: bool = False,
        ):
        self.campaign = campaign
        self.dry_run = dry_run
        self.current_limit = self.set_current_limit()
        self.status_current_limit = self.set_current_limit()
        self.cache_followers = cache_followers

    def set_current_limit(self):
        try:
            return config.messenger__campaign__dm_limit
        except AttributeError as e:
            logger.error("'messenger__campaign__dm_limit' not set", e)
            return 100

    def get_api(self):
        return get_api(username=self.campaign.account.screen_name_tag())

    def datetime_ok(self):
        start = self.campaign.start
        end = self.campaign.end
        if not start and not end:
            return True
        now = timezone.now()
        if start and not end:
            return start <= now
        elif end and not start:
            return now <= end
        else:
            return (
                self.campaign.start < now
                and self.campaign.end > now
            )

    def start(self):
        logger.debug(f'{self.campaign=}')
        bot_su = self.campaign.account
        if not bot_su:
            logger.debug(
                f"No account set for campaign {self.campaign.name}, aborting."
            )
            return
        if not self.campaign.active:
            logger.warn(
                f"{self.campaign.name} is not active."
            )
            return
        if not self.datetime_ok():
            logger.warn(
                f"{self.campaign.name} is not current."
            )
            return
        bot_screen_name = bot_su.screen_name_tag()
        update_social_ids(
            bot_su,
            cached=self.cache_followers,
            bot_screen_name=bot_screen_name,
            relationship="followers",    
        )
        recipient_qs = self.get_recipients()
        logger.debug(f'{recipient_qs=} count={recipient_qs.count()}')
        ThroughModel = Campaign.recipients.through
        ThroughModel.objects.bulk_create(
            [ThroughModel(socialuser_id=su.id, campaign_id=self.campaign.id) for su in recipient_qs],
            ignore_conflicts=True
        )
        self.campaign.refresh_from_db()
        logger.debug(
            f'{self.campaign.recipients.all()=}'
            f'{self.campaign.recipients.all().count()=}'    
        )
        if not self.dry_run:
            self.send()
            if self.campaign.send_status:
                self.send_status()

    def get_recipients(self):
        bot_su = self.campaign.account
        bot_follower_id = Follower.objects.filter(user=bot_su).latest().id_list
        logger.debug(f'{bot_follower_id=}')
        qs = SocialUser.objects.filter(user_id__in=bot_follower_id)
        logger.debug(f'no filter: {qs=} count={qs.count()=}')
        logger.debug(f'{self.campaign.restrict_by_category=}')
        if self.campaign.restrict_by_category is not None:
            qs = self.filter_category(qs)
            logger.debug(f'restrict_by_category: {qs=} count={qs.count()=}')
        if self.campaign.crowdfunding.all():
            qs = self.filter_crowdfunding(qs)
        logger.debug(f'{self.campaign.retweet_range=}')
        if self.campaign.restrict_by_last_investment:
            qs = self.filter_last_investment(qs)
        if self.campaign.retweet_range:
            qs = self.filter_retweet_range(qs)
            logger.debug(f'filter_retweet_range: {qs=} count={qs.count()=}')
        return qs

    def filter_category(self, qs):
        ids = []
        for category in self.campaign.categories.all():
            ids.extend(
                category.socialuser_set.values_list("id", flat=True)
            )
        # remove None items
        ids = list(filter(None, ids))
        if self.campaign.restrict_by_category:
            qs = qs.filter(id__in=ids)
        else:
            qs = qs.exclude(id__in=ids)
        return qs

    def filter_crowdfunding(self, qs):
        include_id_set = set()
        exclude_id_set = set()
        for index, cc in enumerate(self.campaign.crowdfunding.all()):
            _su = ProjectInvestment.objects.filter(
                paid=True,
                datetime__gte=cc.start_datetime,
                datetime__lte=cc.end_datetime,
                project=cc.project
            ).values_list("user__socialuser__id", flat=True)
            ids=list(_su)
            # remove None items
            ids = list(filter(None, ids))
            logger.debug(f'{ids=}')
            mc = MessengerCrowdfunding.objects.get(
                messenger_campaign=self.campaign,
                crowdfunding_campaign=cc
            )
            logger.debug(f'{mc=} {mc.toggle=}')
            if mc.toggle:
                logger.debug("filter")
                if self.campaign.crowdfunding_and:
                    if index==0:
                        include_id_set.update(set(ids))
                    else:
                        include_id_set.intersection_update(set(ids))
                else:
                    include_id_set.update(set(ids))
            else:
                logger.debug("exclude")
                if self.campaign.crowdfunding_and:
                    if index==0:
                        exclude_id_set.update(set(ids))
                    else:
                        exclude_id_set.intersection_update(set(ids))
                else:
                    exclude_id_set.update(set(ids))
            logger.debug(f'{include_id_set=}\n{exclude_id_set=}')

        if self.campaign.crowdfunding_and:
            qs = qs.filter(id__in=include_id_set)
            if exclude_id_set:
                qs = qs.exclude(id__in=exclude_id_set)
        else:
            qs = qs.filter(id__in=include_id_set)
            if exclude_id_set:
                qs = qs | qs.exclude(id__in=exclude_id_set)
        return qs

    def filter_last_investment(self, qs):
        """
        Select users who participated to campaigns included in 'crowdfunding'
        field where toggle is True, except those who participated less than
        'restrict_by_last_investment' duration ago.
        """
        cutoff: datetime.datetime = (
            timezone.now() - self.campaign.restrict_by_last_investment
        )
        if self.campaign.crowdfunding.all():
            for cc in self.campaign.crowdfunding.filter(
                messengercrowdfunding__toggle=True
            ):
                _su = ProjectInvestment.objects.filter(
                    paid=True,
                    datetime__gt=cutoff,
                    project=cc.project
                ).values_list("user__socialuser__id", flat=True)
                ids=list(_su)
                # remove None items
                ids = list(filter(None, ids))
                qs = qs.filter(~Q(id__in=ids))
        else:
            _su = ProjectInvestment.objects.filter(
                paid=True,
                datetime__gt=cutoff,
                project__in=self.campaign.crowdfunding_project.all()
            ).values_list("user__socialuser__id", flat=True)
            ids=list(_su)
            # remove None items
            ids = list(filter(None, ids))
            qs = qs.filter(~Q(id__in=ids))
        return qs

    def filter_retweet_range(self, qs):
        rt_range = self.campaign.retweet_range
        filtered_su_ids = []
        #su_ids = qs.values_list("id", flat=True)
        bot_su = self.campaign.account
        tweetdj_rt_by_bot_qs = Tweetdj.objects.filter(retweeted_by=bot_su)
        for su in qs:
            count = tweetdj_rt_by_bot_qs.filter(socialuser=su).count()
            if count in rt_range:
                filtered_su_ids.append(su.id)
        qs = qs.filter(id__in=filtered_su_ids)
        return qs

    def send(self):
        messages = self.campaign.messages.all()
        api = self.get_api()
        if not api:
            return
        for recipient in self.campaign.recipients.all():
            if self.current_limit <= 0:
                return
            for message in messages:
                message_manager = MessageManager(
                    campaign=self.campaign,
                    message=message,
                    recipient=recipient,
                    api=api
                )
                result = message_manager.create()
                if result is False:
                    return
                if result is True:
                    self.current_limit-=1
                    self.sleep_random()
                if result is None:
                    continue

    def send_status(self):
        if not self.campaign.status:
            return
        api = self.get_api()
        if not api:
            return
        for recipient in self.campaign.recipients.all():
            if self.status_current_limit <= 0:
                return
            status_manager = StatusManager(
                campaign=self.campaign,
                recipient=recipient,
                api=api
            )
            result = status_manager.update()
            if result is True:
                self.current_limit-=1
            elif result is False:
                return           

    def randinterval(self):
        backoff = self.campaign.backoff
        if backoff <= 0:
            return
        variance = backoff*0.1
        return random.randint(
            int(round(backoff-variance)),
            int(round(backoff+variance))
        )

    def sleep_random(self):
        duration = self.randinterval()
        if not duration:
            return
        time.sleep(duration)


class MessageManager:
    def __init__(
            self,
            campaign: Campaign,
            message: Message,
            recipient: SocialUser,
            api
    ):
        self.campaign = campaign
        self.message = message
        self.recipient = recipient
        self.sender = self.campaign.account
        self.api = api
        self.text = None
        self.retweeted_qs = Tweetdj.objects.filter(
            retweeted_by=self.sender,
            socialuser=self.recipient
        )

    def is_message_sent(self):
        if self.has_valid_receipt():
            return True
        if self.dm_exists():
            return True

    @classmethod
    def replace_special_char(cls, s):
        # class or instance object accessible through cls
        regex = re.compile(r'[\n\r\t]')
        s = regex.sub('', s)
        s = s.replace(' ', '')
        return s

    def dm_exists(self):
        sender_id=self.sender.user_id
        recipient_id=self.recipient.user_id
        screen_name=self.recipient.screen_name_tag()
        logger.debug(
            f'{sender_id=}, {recipient_id=}, {self.text=}, {screen_name=}'
        )
        dm_qs = DirectMessage.objects.filter(
            sender_id=sender_id,
            recipient_id=recipient_id,
            text__icontains=screen_name,
            created_timestamp__gte=datetime.datetime.timestamp(
                self.campaign.created
            )*1000
        )
        logger.debug(f'{dm_qs=}')
        clean_text = MessageManager.replace_special_char(self.text)
        for dm in dm_qs:
            if MessageManager.replace_special_char(dm.text) == clean_text:
                logger.debug(f'{dm}=')
                return True

    def has_valid_receipt(self):
        for receipt in Receipt.objects.filter(
            campaign = self.campaign,
            message = self.message,
            user = self.recipient
        ):
            if receipt.event_id:
                return True

    def activate_language(self):
        try:
            community = self.campaign.account.account.community
        except:
            community = None
        if community:
            activate_language(community)

    def first_retweet_date(self) -> str:
        self.activate_language()
        try:
            community = self.campaign.account.account.community
        except:
            community = None
        if community:
            activate_language(community)
        try:
            dt = self.retweeted_qs.earliest('statusid').created_at
            return date_format(dt, format='DATE_FORMAT', use_l10n=True)
        except Tweetdj.DoesNotExist:
            return

    def site_url(self) -> str:
        community = self.sender.account.community
        return site_url(community)

    def investment_date(self) -> str:
        self.activate_language()
        projects : list[Project] = [
            cf.project for cf in self.campaign.crowdfunding.all()
        ]
        qs = (ProjectInvestment.objects
            .filter(
                user__in=self.recipient.user_set.all(),
                project__in=projects,
                paid=True,
            )
            .order_by('datetime', 'uuid')
            .distinct('datetime', 'uuid')
            .values_list('datetime', flat=True)
        )
        if not qs:
            return ""
        dt_str: list[str] = [
            date_format(dt, format='DATE_FORMAT', use_l10n=True)
            for dt in qs
        ]
        if len(dt_str) == 1:
            return dt_str[0]
        elif len(dt_str) == 2:
            return " & ".join(dt_str)
        else:
            return ", ".join(dt_str[:-1]) + " & " + dt_str[-1]

    def _format(self):
        try:
            screen_name = self.recipient.screen_name_tag()
        except Profile.DoesNotExist:
            create_update_profile_twitter(
                self.recipient,
                bot_screen_name=self.sender.screen_name_tag(),
                cache=False
            )
            self.recipient.refresh_from_db()
            screen_name = self.recipient.screen_name_tag()

        d = {
            'screen_name' : screen_name,
            'bot_screen_name' : self.sender.screen_name_tag(),
            'retweet_count' : self.retweeted_qs.count(),
            'first_retweet_date' : self.first_retweet_date(),
            'site_url' : self.site_url(),
            'investment_date': self.investment_date(),
        }
        return self.message.content.format(**d)

    def create(self):
        self.text=self._format()
        if self.is_message_sent():
            return
        try:
            receipt = Receipt.objects.create(
                campaign=self.campaign,
                message=self.message,
                user=self.recipient
            )
        except:
            return
        try:
            res = self.api.send_direct_message(
                recipient_id=self.recipient.user_id,
                text=self.text
            )
            logger.debug(res)
            receipt.event_id=res.id
            receipt.save()
            return True
        except TweepError as e:
            logger.error(f"addstatus: Tweepy error: {e}")
            try:
                error_code =  e.args[0][0]['code']
            except:
                error_code = 0
            receipt.error = error_code
            receipt.save()
            if error_code in [420, 429, 88, 226]:
                return False




class StatusManager:
    def __init__(
            self,
            campaign: Campaign,
            recipient: SocialUser,
            api
    ):
        self.campaign = campaign
        self.status = campaign.status
        self.recipient = recipient
        self.sender: SocialUser = self.campaign.account
        self.api = api

    def screen_name(self):
        delta = datetime.timedelta(
            days=config.messenger_status_screen_name_delta_days
        )
        return recent_twitter_screen_name(
            self.recipient.user_id,
            self.sender.user_id,
            delta
        )

    def dm_url(self):
        return (
            f'https://twitter.com/messages/'
            f'{self.sender.user_id}-{self.recipient.user_id}'
        )

    def dm_dl(self):
        return (
            'https://twitter.com/messages/compose'
            f'?recipient_id={self.sender.user_id}'
        )

    def status_exists(self):
        return StatusLog.objects.filter(
            campaign = self.campaign,
            user = self.recipient,
            statusid__isnull=False
        ).exists()

    def dtd_ok(self):
        qs = Receipt.objects.filter(
            campaign=self.campaign,
            user=self.recipient,
            event_id__isnull=False
        )
        if not qs:
            return False
        dm_dt: datetime.datetime = qs.latest('created').created
        now = timezone.now()
        delta = self.campaign.status_delay
        return (now - dm_dt) > delta

    def compose(self):
        screen_name = self.screen_name()
        if not screen_name:
            return
        status_content = self._format()
        if not status_content:
            return
        return f'@{screen_name} {status_content}'

    def _format(self):
        d = {
            'dm_url' : self.dm_url(),
            'dm_dl' : self.dm_dl(),
        }
        return self.status.content.format(**d)

    def update(self):
        if self.status_exists():
            return
        if not self.dtd_ok():
            return
        status = self.compose()
        if not status:
            return
        try:
            status_log = StatusLog.objects.create(
                campaign=self.campaign,
                user=self.recipient,
                status=self.campaign.status,   
            )
        except Exception as e:
            logger.error(e)
            return
        try:
            status = self.api.update_status(status)
            status_log.statusid=status.id
            status_log.save()
            return True
        except TweepError as e:
            logger.error(f"Tweepy error: {e}")
            try:
                error_code =  e.args[0][0]['code']
            except:
                error_code = 0
            status_log.error = error_code
            status_log.save()
            return False