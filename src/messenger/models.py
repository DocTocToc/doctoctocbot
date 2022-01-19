import logging
from django.db import models
from django.contrib.postgres.fields import IntegerRangeField
from moderation.models import SocialUser, Category
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from constance import config

logger = logging.getLogger(__name__)

def validate_status(value):
    try:
        max_chars = config.messenger_status_max_chars
    except:
        return
    logger.debug(f'{value=} {type(value)=}')
    if len(value) > max_chars:
        raise ValidationError(
            _(
                'This text field contains %(current_chars)s characters.'
                'The maximum number of characters allowed is %(max_chars)s.'
            ),
            params={
                'current_chars': str(len(value)),
                'max_chars': max_chars,
            },
        )


class Status(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True
    )
    content = models.TextField(
        validators=[validate_status]
    )
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Status {self.name} ({self.created})"

    
    class Meta:
        verbose_name_plural = "Statuses"


class StatusLog(models.Model):
    campaign = models.ForeignKey(
        'messenger.Campaign',
        verbose_name    = _('Campaign'),
        help_text           = _('Campaign linked to this log.'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    status = models.ForeignKey(
        'messenger.Status',
        verbose_name    = _('Status'),
        help_text           = _('Status linked to this log.'),
        related_name = "log",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        SocialUser,
        verbose_name    = _('User'),
        help_text           = _('Status is a reply to this user'),
        on_delete=models.CASCADE,
    )
    statusid = models.BigIntegerField(
        verbose_name = _('Status id'),
        help_text = _('Status id of the reply.'),
        null=True,
        blank=True,
        default=None,
    )
    error = models.TextField(
        verbose_name = _('Error message'),
        help_text = _('Error message recorded if the status was not created.'), 
    )
    created =  models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = _(u"StatusLog")
        verbose_name_plural = _("StatusLogs")

    def __str__(self):
        return (
            f"Log for campaign {self.campaign} and user {self.user} "
            f"{self.error}"
        )


class Message(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True
    )
    content = models.TextField(
        blank=True,
        null=True
    )
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ['created',]
    
    def __str__(self):
        return f"Message {self.name} ({self.created})"


def get_backoff():
    return config.messenger__models__backoff_default


class MessengerCrowdfunding(models.Model):
    """Through model between messenger.Campaign and crowdfunding.Campaign
    """
    messenger_campaign = models.ForeignKey(
        "messenger.Campaign",
        on_delete=models.PROTECT,
    )
    crowdfunding_campaign = models.ForeignKey(
        "crowdfunding.Campaign",
        on_delete=models.PROTECT,
    )
    toggle = models.BooleanField(
        null=True,
        help_text=(
            "When set to True, message will be sent to users who participated "
            "to this crowdfunding campaign. When set to False, message will "
            "not be sent to users who participated to this crowdfunding "
            "campaign."
        )
    )

    def __str__(self):
        return (
            f'MessengerCrowdfunding {self.pk}. '
            f'{self.messenger_campaign.name} - '
            f'{self.crowdfunding_campaign.project.name} '
            f'({self.crowdfunding_campaign.start_datetime.date().isoformat()}-'
            f'{self.crowdfunding_campaign.end_datetime.date().isoformat()})'
        )


class Campaign(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True
    )
    account = models.ForeignKey(
        SocialUser,
        related_name="campaign_account",
        on_delete=models.SET_NULL,
        null=True
    )
    restrict_by_category = models.BooleanField(
        null=True,
        blank=True
    )
    categories = models.ManyToManyField(
        Category,
        blank=True,
    )
    restrict_by_crowdfunding = models.BooleanField(
        null=True,
        blank=True
    )
    crowdfunding_campaign = models.ManyToManyField(
        'crowdfunding.Campaign',
        blank=True,
    )
    crowdfunding = models.ManyToManyField(
        'crowdfunding.Campaign',
        through='MessengerCrowdfunding',
        related_name="messenger_campaigns",
    )
    retweet_range = IntegerRangeField(
        blank=True,
        null=True,
        help_text = _(
            u'Min and/or max retweet(s) required to send msg. Bounds: [)'
        )    
    )
    recipients = models.ManyToManyField(
        SocialUser,
        blank=True
    )
    messages = models.ManyToManyField(
        Message,
        through             = 'CampaignMessage',
        related_name    = 'messages',
        verbose_name    = _(u'Messages'),
        help_text           = _(u'Messages from this Campaign')
    )
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)
    backoff = models.PositiveIntegerField(
        default = get_backoff,
        help_text = "period between 2 API message_create events in seconds"
    )
    active = models.BooleanField(
        default=True,
    )
    start = models.DateTimeField(
        null=True,
        blank=True,
    )
    end = models.DateTimeField(
        null=True,
        blank=True,
    )
    send_status = models.BooleanField(
        null=True,
        blank=True,
    )
    status_delay = models.DurationField(
        null=True,
        blank=True
    )
    status = models.ForeignKey(
        'messenger.Status',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )


    class Meta:
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")
        ordering = ['created',]
    
    def __str__(self):
        return f"Campaign {self.name} ({self.created})"

class Receipt(models.Model):
    campaign = models.ForeignKey(
        Campaign,
        verbose_name    = _('Campaign'),
        help_text           = _('Campaign linked to this receipt.'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    message = models.ForeignKey(
        Message,
        verbose_name    = _('Message'),
        help_text           = _('Receipt for this message.'),
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        SocialUser,
        verbose_name    = _('User'),
        help_text           = _('Receipt for a message sent to this user'),
        on_delete=models.CASCADE,
    )
    event_id = models.BigIntegerField(
        verbose_name = _('DM event id'),
        help_text = _('DM event id created if the message was successfully sent.'),
        null=True,
        blank=True,
        default=None,
    )
    error = models.TextField(
        verbose_name = _('Error message'),
        help_text = _('Error message recorded if the message was not successfully sent.'),
        null=True,
        blank=True,  
    )
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _(u"Receipt")
        verbose_name_plural = _("Receipts")

    def __str__(self):
        return (
            f"Message {self.message} "
        )


class CampaignMessage(models.Model):
    campaign = models.ForeignKey(
        Campaign,
        verbose_name    = _('Campaign'),
        help_text           = _('Messages are part of this campaign.'),
        on_delete=models.CASCADE,
    )
    message = models.ForeignKey(
        Message,
        verbose_name    = _('Message'),
        help_text           = _('Messages are part of this campaign.'),
        on_delete=models.CASCADE,
    )
    order = models.IntegerField(
        verbose_name    = _(u'Order'),
        help_text           = _(u'What order to display this person within the department.'),
    )

    class Meta:
        verbose_name = _(u"Campaign Message")
        verbose_name_plural = _(u"Campaign Messages")
        ordering = ['order',]
        unique_together = ('campaign', 'order')

    def __str__(self):
        return (
            f"Message {self.message.name} "
            f"from campaign {self.campaign.name} "
            f"with order {self.order}"
        )

