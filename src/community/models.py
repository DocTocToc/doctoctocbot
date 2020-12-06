from django.db import models
from django.contrib.sites.models import Site
import logging
from django.conf import settings
import reversion

from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class Community(models.Model):
    name = models.CharField(max_length=101, unique=True)
    active = models.BooleanField(default=False)
    account = models.OneToOneField(
        'bot.Account',
        on_delete=models.CASCADE,
        related_name='community',
    )
    hashtag = models.ManyToManyField('conversation.Hashtag')
    membership = models.ManyToManyField(
        'moderation.Category',
        related_name='member_of',
        blank=True,
    )
    created =  models.DateTimeField(auto_now_add=True)
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        null=True,
        related_name="community",
    )
    trust = models.ManyToManyField(
        'self',
        through='Trust',
        through_fields=('from_community', 'to_community'),
        symmetrical=False,
        related_name='trusted_by',
        blank=True,
        
    )
    cooperation = models.ManyToManyField(
        'self',
        through='Cooperation',
        through_fields=('from_community', 'to_community'),
        symmetrical=False,
        related_name='cooperating_with',
        blank=True,
    )
    category = models.ManyToManyField(
        'moderation.Category',
        through='CommunityCategoryRelationship',
        related_name='community',
        blank=True,
    )
    crowdfunding = models.ForeignKey(
        'crowdfunding.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="community",
    )
    helper = models.ForeignKey(
        'bot.Account',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="helper_community",
    )
    helper_message = models.TextField(
        max_length=200,
        blank=True,
        null=True,
    )
    allow_unknown = models.BooleanField(
        default=False,
    )
    language = models.CharField(
        max_length=3,
        blank=True,
        help_text="ISO language code",
    )
    pending_moderation_period = models.PositiveIntegerField(
        default = 0,
        help_text = "Pending moderation period (hour)"
    )
    viral_moderation = models.BooleanField(
        default=False,
        help_text = "Does a verified follower immediately become a moderator?",
    )
    viral_moderation_category = models.ManyToManyField(
        'moderation.Category',
        related_name='viral_moderation_community',
        blank=True,
    )
    viral_moderation_message = models.TextField(
        blank=True,
        null=True,
    )
    tree_search = models.BooleanField(
        default=False,
        help_text = (
            "Launch a conversation tree nodes search based on Twitter API "
            "for this community at startup"
        )
    )
    no_root_backoff = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text = "tree_search backoff period after no root found (second)"
    )
    tree_search_retry = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text = "minimum retry period after all roots processed (second)"
    )
    verification_threshold_follower = models.PositiveIntegerField(
        default = settings.VERIFICATION_THRESHOLD_FOLLOWER,
        help_text = "Start verification if follower count superior or equal to"
    )
    follower = models.ManyToManyField(
        'moderation.Category',
        related_name='follower_of',
        blank=True,
        help_text='Categories authorized to follow the account if protected'
    )
    follow_request_backoff = models.PositiveIntegerField(
        default = 1,
        help_text = (
            "Period in hour during which a follow request will be "
            "automatically declined if the previous one was declined."
        )
    )
    request_queue_backoff = models.PositiveIntegerField(
        default = 30,
        help_text = (
            "For a given user, wait this amount of time after one of its "
            " queues was modified before a new queue can be created."
        )
    )
    follower_common_account = models.ManyToManyField(
        'bot.Account',
        related_name='follower_common_account_community',
        help_text = (
            "These Accounts are part of a common follower community for "
            "retweeting purpose. If a user follows one of those accounts, she "
            "will be retweeted by the current Account."    
        )   
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "communities"


def get_default_community():
    return None


class Retweet(models.Model):
    community = models.ForeignKey('Community', on_delete=models.CASCADE)
    hashtag = models.ForeignKey('conversation.Hashtag', on_delete=models.CASCADE)
    category = models.ForeignKey(
        'moderation.Category',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    retweet = models.BooleanField(default=False)
    moderation = models.BooleanField(default=True)
    require_question = models.BooleanField(default=True)
    allow_retweet = models.BooleanField(default=False)
    allow_quote = models.BooleanField(default=False)
    require_follower = models.BooleanField(default=True)


    def __str__(self):
        return "{} - {} - {} : {}".format(self.community, self.hashtag, self.category, self.retweet)


    class Meta:
        unique_together = ("community", "hashtag", "category")

    
class Trust(models.Model):
    '''
    The Trust through model contains information about which community trusts which
    other community about the moderation of which categories of social users.
    The trusted community must authorize the use of its moderation data.
    :param from_community: community which creates the Trust object
    :param category: Category which is the subject of the trust relationship
    :param to_community: community trusted by the from_community
    :param authorization: has the trusted community given the from_community its
    authorization to use its moderation data?
    '''
    from_community = models.ForeignKey(
        'Community',
        on_delete=models.CASCADE,
        related_name='trust_from',
    )
    category = models.ForeignKey('moderation.Category', on_delete=models.CASCADE)
    to_community = models.ForeignKey(
        'Community',
        on_delete=models.CASCADE,
        related_name='trust_to',
    )
    created =  models.DateTimeField(auto_now_add=True)
    authorized = models.BooleanField(default=False)

    def __str__(self):
        return "{_from} trusts {to} about {category} : {authorized}".format(
            _from=self.from_community,
            to=self.to_community,
            category=self.category,
            authorized=self.authorized
        )

    class Meta:
        unique_together = ("from_community", "to_community", "category")

    
class Cooperation(models.Model):
    from_community = models.ForeignKey(
        'Community',
        on_delete=models.CASCADE,
        related_name='cooperation_from',
    )
    to_community = models.ForeignKey(
        'Community',
        on_delete=models.CASCADE,
        related_name='cooperation_to',
    )
    created =  models.DateTimeField(auto_now_add=True)
    authorized = models.BooleanField(default=False)  
    
    def __str__(self):
        return "{_from} trusts {to}: {authorized}".format(
            _from=self.from_community,
            to=self.to_community,
            authorized=self.authorized
        )
        
    class Meta:
        unique_together = ("from_community", "to_community")


class CommunityCategoryRelationship(models.Model):
    community = models.ForeignKey(
        'Community',
        on_delete=models.CASCADE,
        related_name='category_relationship', 
    )
    category = models.ForeignKey(
        'moderation.Category',
        on_delete=models.CASCADE,
        related_name='community_relationship',
    )
    quickreply = models.BooleanField(
        default=False,
        help_text="Include in DM quickreply?"
    )
    socialgraph = models.BooleanField(
        default=False,
        help_text="Include in moderation social graph?"
    )    
    color = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"community: {self.community.name} - category: {self.category.name}"
    
    class Meta:
        unique_together = ("community", "category")


class TextDescription(models.Model):
    name = models.CharField(
        max_length=254,
        unique=True,
    )
    label = models.CharField(
        max_length=254,
    )
    description = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.label}"


@reversion.register(fields='content')
class Text(models.Model):
    community = models.ForeignKey(
        'Community',
        on_delete=models.CASCADE,
        related_name='text',
    )
    type = models.ForeignKey(
        'TextDescription',
        on_delete=models.CASCADE,
        related_name='text',
    )
    content = models.TextField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Text: community = {self.community} type = {self.type}"


    class Meta:
        unique_together = ("community", "type")
        

class AccessLevel(models.Model):
    """API access level categories.
    """
    name = models.CharField(
        max_length=254,
        unique=True,
    )
    label = models.CharField(
        max_length=254,
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    
    def __str__(self):
        return f"{self.label}"


class ApiAccess(models.Model):
    """API access for each access level
    """
    community = models.ForeignKey(
        'Community',
        on_delete=models.CASCADE,
        related_name='api_access',
    )
    level = models.ForeignKey(
        'AccessLevel',
        on_delete=models.CASCADE,
        related_name='api_access',
    )
    status_limit = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        verbose_name=_('Status limit'),
        help_text=_('Total number of status.'),
    )
    status_rate = models.IntegerField(
        blank=True,
        null=True,
        default=0,
        verbose_name=_('Status rate (per minute)'),
        help_text=_('Number of status per minute.'),
    )
    author_category = models.BooleanField(
        default=False,
        verbose_name=_('Author category'),
        help_text=_("Category of the author of the status."),
    )
    author_specialty = models.BooleanField(
        default=False,
        verbose_name=_('Author specialty'),
        help_text=_("Specialty of the author of the status."),
    )
    search_datetime = models.BooleanField(
        default=False,
        verbose_name=_('Date and Time search'),
        help_text=_("Search status by date and time."),
    )
    search_category = models.BooleanField(
        default=False,
        verbose_name=_('Category search'),
        help_text=_("Search status by category."),
    )
    search_tag = models.BooleanField(
        default=False,
        verbose_name=_('Tag search'),
        help_text=_("Search status by tag."),
    )
    status_category = models.BooleanField(
        default=False,
        verbose_name=_('Status category'),
        help_text=_("Access status category."),
    )
    status_tag = models.BooleanField(
        default=False,
        verbose_name=_('Status tag'),
        help_text=_("Access status tag."),
    )
    status_protected = models.BooleanField(
        default=False,
        verbose_name=_('Protected status'),
        help_text=_("Access status from protected account."),
    )
    status_media = models.BooleanField(
        default=False,
        verbose_name=_('Status media'),
        help_text=_("Access status media."),
    )

    def __str__(self):
        return f"API Access: community = {self.community} ; level = {self.level}"


    class Meta:
        unique_together = ("community", "level")