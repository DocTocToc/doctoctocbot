import logging
import random
import time
import datetime
import re

from constance import config
from tweepy import TweepError

from django.db.models import Q
from django.utils.formats import date_format
from community.helpers import activate_language

from dm.models import DirectMessage
from bot.tweepy_api import get_api
from moderation.social import update_social_ids
from messenger.models import Campaign, Receipt, Message
from moderation.models import SocialUser, Follower
from crowdfunding.models import ProjectInvestment
from conversation.models import Tweetdj

logger = logging.getLogger(__name__)


class CampaignManager:
    def __init__(self, campaign: Campaign):
        self.campaign = campaign
        self.current_limit = self.set_current_limit()

    def set_current_limit(self):
        try:
            return config.messenger__campaign__dm_limit
        except AttributeError as e:
            logger.error("'messenger__campaign__dm_limit' not set", e)
            return 100

    def get_api(self):
        return get_api(
            username=self.campaign.account.screen_name_tag(),
            backend=True,
        )

    def start(self):
        logger.debug(f'{self.campaign=}')
        bot_su = self.campaign.account
        if not bot_su:
            logger.debug(
                f"No account set for campaign {self.campaign.name}, aborting."
            )
            return
        bot_screen_name = bot_su.screen_name_tag()
        update_social_ids(
            bot_su,
            cached=True,
            bot_screen_name=bot_screen_name,
            relationship="followers",    
        )
        recipient_qs = self.get_recipients()
        logger.debug(f'{recipient_qs=}')
        ThroughModel = Campaign.recipients.through
        ThroughModel.objects.bulk_create(
            [ThroughModel(socialuser_id=su.id, campaign_id=self.campaign.id) for su in recipient_qs],
            ignore_conflicts=True
        )
        self.campaign.refresh_from_db()
        logger.debug(f'{self.campaign.recipients.all()=}')
        
        self.send()

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
        logger.debug(f'{self.campaign.restrict_by_crowdfunding=}')
        if self.campaign.restrict_by_crowdfunding is not None:
            qs = self.filter_crowdfunding(qs)
            logger.debug(f'restrict_by_crowdfunding: {qs=} count={qs.count()=}')
        logger.debug(f'{self.campaign.retweet_range=}')
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
        ids = []
        for cc in self.campaign.crowdfunding_campaign.all():
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
        if self.campaign.restrict_by_crowdfunding:
            logger.debug("filter")
            qs = qs.filter(id__in=ids)
        else:
            logger.debug("exclude")
            qs = qs.filter(~Q(id__in=ids))
        return qs

    def filter_retweet_range(self, qs):
        range = self.campaign.retweet_range
        filtered_su_ids = []
        #su_ids = qs.values_list("id", flat=True)
        bot_su = self.campaign.account
        tweetdj_rt_by_bot_qs = Tweetdj.objects.filter(retweeted_by=bot_su)
        for su in qs:
            count = tweetdj_rt_by_bot_qs.filter(socialuser=su).count()
            if count in range:
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
                if result is True:
                    self.current_limit-=1
                elif result is False:
                    return


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

    def first_retweet_date(self) -> str:
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

    def _format(self):
        d = {
            'screen_name' : self.recipient.profile.screen_name_tag(),
            'retweet_count' : self.retweeted_qs.count(),
            'first_retweet_date' : self.first_retweet_date(),
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
            self.sleep_random()
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