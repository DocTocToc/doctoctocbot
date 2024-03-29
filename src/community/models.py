from datetime import timedelta
from django.db import models
from django.contrib.sites.models import Site
import logging
from django.conf import settings
import reversion
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class CommunityManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Community(models.Model):
    name = models.CharField(
        max_length=101,
        unique=True
    )
    active = models.BooleanField(default=False)
    account = models.OneToOneField(
        'bot.Account',
        on_delete=models.CASCADE,
        related_name='community',
    )
    mastodon_account = models.OneToOneField(
        'moderation.MastodonUser',
        on_delete=models.PROTECT,
        related_name='community',
        blank=True,
        null=True,
    )
    mastodon_access = models.OneToOneField(
        'fediverse.MastodonAccess',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    hashtag = models.ManyToManyField('conversation.Hashtag')
    membership = models.ManyToManyField(
        'moderation.Category',
        related_name='member_of',
        blank=True,
    )
    created =  models.DateTimeField(auto_now_add=True)
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
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
    crowdfunding = models.OneToOneField(
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
        max_length=257,
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
    pending_moderation_period = models.DurationField(
        null = True,
        blank = True,
        default = timedelta,
        help_text = "Duration before moderation sent to other moderator " \
                    "Format: [DD] [HH:[MM:]]ss[.uuuuuu]"
    )
    pending_self_moderation_period = models.DurationField(
        null = True,
        blank = True,
        default = timedelta,
        help_text = "Duration before self moderation sent again " \
                    "Format: [DD] [HH:[MM:]]ss[.uuuuuu]"
    )
    moderator_moderation_period = models.DurationField(
        null=True,
        blank=True,
        help_text = "Interval before same moderation sent again to moderator"
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
    follow_request_backoff = models.DurationField(
        null=True,
        blank=True,
        help_text = (
            "Period during which a follow request will be "
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
        blank=True,
        help_text = (
            "These Accounts are part of a common follower community for "
            "retweeting purpose. If a user follows one of those accounts, she "
            "will be retweeted by the current Account."    
        ),
    )
    twitter_follow_member = models.BooleanField(
        default=False,
        help_text = (
            "Bot's Twitter account will follow the members of this community."
        )
    )
    twitter_request_dm = models.BooleanField(
        default=False,
        help_text = (
            "Twitter account will attempt to send a DM after a follow request."
        )
    )
    twitter_request_dm_text = models.TextField(
        blank=True,
        null=True,
    )
    twitter_self_moderation_dm = models.TextField(
        blank=True,
        null=True,
    )
    blog = models.ForeignKey(
        'community.Blog',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="community",
    )
    members_friends_cache = models.DurationField(
        null=True,
        blank=True,
        help_text = (
            "Duration of cache for members' friends set"
        )
    )
    twitter_creator = models.ForeignKey(
        'moderation.SocialUser',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    admins = models.ManyToManyField(
        'moderation.Entity',
        related_name='admin_of_communities',
        blank=True,
    )

    objects = CommunityManager()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "communities"


    def natural_key(self):
        return (self.name,)


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
    favorite = models.BooleanField(default=False)
    moderation = models.BooleanField(default=True)
    require_question = models.BooleanField(default=True)
    allow_retweet = models.BooleanField(default=False)
    allow_quote = models.BooleanField(default=False)
    require_follower = models.BooleanField(default=False)
    require_friend = models.BooleanField(default=False)


    def __str__(self):
        return "{} - {} - {} : {}".format(self.community, self.hashtag, self.category, self.retweet)


    class Meta:
        unique_together = ("community", "hashtag", "category")


class Reblog(models.Model):
    community = models.ForeignKey(
        'Community',
        on_delete=models.CASCADE
    )
    hashtag = models.ForeignKey(
        'conversation.Hashtag',
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        'moderation.Category',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    reblog = models.BooleanField(default=False)
    favourite = models.BooleanField(default=False)
    bookmark = models.BooleanField(default=False)
    moderation = models.BooleanField(default=False)
    require_question = models.BooleanField(default=False)
    allow_reblogged = models.BooleanField(default=False)
    require_follower = models.BooleanField(default=False)
    require_following = models.BooleanField(default=False)

    def __str__(self):
        return "<{} - {} - {}>".format(self.community, self.hashtag, self.category)


    class Meta:
        unique_together = ("community", "hashtag", "category")


class TrustManager(models.Manager):
    def get_by_natural_key(
            self,
            from_community_name,
            to_community_name,
            category_name,
        ):
        return self.get(
            from_community__name=from_community_name,
            to_community__name=to_community_name,
            category__name=category_name
        )


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

    objects = TrustManager()

    def __str__(self):
        return "{_from} trusts {to} about {category} : {authorized}".format(
            _from=self.from_community,
            to=self.to_community,
            category=self.category,
            authorized=self.authorized
        )

    class Meta:
        unique_together = ("from_community", "to_community", "category")


    def natural_key(self):
        return (
            self.from_community.natural_key()
            + self.to_community.natural_key()
            + self.category.natural_key()
        )


class CooperationManager(models.Manager):
    def get_by_natural_key(
            self,
            from_community_name,
            to_community_name,
        ):
        return self.get(
            from_community__name=from_community_name,
            to_community__name=to_community_name,
        )


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

    objects = CooperationManager()

    def __str__(self):
        return "{_from} trusts {to}: {authorized}".format(
            _from=self.from_community,
            to=self.to_community,
            authorized=self.authorized
        )
        
    class Meta:
        unique_together = ("from_community", "to_community")


    def natural_key(self):
        return (
            self.from_community.natural_key()
            + self.to_community.natural_key()
        )


class CommunityCategoryRelationshipManager(models.Manager):
    def get_by_natural_key(self, community_name, category_name):
        return self.get(
            community__name=community_name,
            category__name=category_name,
        )


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
    quickreply_self = models.BooleanField(
        default=False,
        help_text="Include in self moderation?"
    )  
    socialgraph = models.BooleanField(
        default=False,
        help_text="Include in moderation social graph?"
    )
    do_not_follow = models.BooleanField(
        default=False,
        help_text="Bot should not follow SocialUsers from this category"
    )
    follower_chart = models.BooleanField(
        default=False,
        help_text="Add this category to the follower chart"
    )
    color = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    objects = CommunityCategoryRelationshipManager()

    def __str__(self):
        return f"community: {self.community.name} - category: {self.category.name}"
    
    class Meta:
        unique_together = ("community", "category")


    def natural_key(self):
        return (self.community.natural_key() + self.category.natural_key())


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
    community = models.ManyToManyField(
        'Community',
        through='TextCommunity',
        through_fields=('text', 'community'),
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
        communities = ", ".join(str(community) for community in self.community.all())
        return f"Text: community = {communities} type = {self.type}"


    class Meta:
        pass


class TextCommunity(models.Model):
    text = models.ForeignKey(Text, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)

    def validate_unique(self, *args, **kwargs):
        super(TextCommunity, self).validate_unique(*args, **kwargs)
        qs = Text.objects.filter(community=self.community)
        if qs.filter(type=self.text.type).exclude(pk=self.text.pk).exists():
            raise ValidationError(
                {
                    'community':[
                        'Type and Community must be unique together per Text '
                        f'({qs.filter(type=self.text.type)})',
                    ]
                }
            )


class AccessLevelManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


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
    
    objects = AccessLevelManager()

    def __str__(self):
        return f"{self.label}"
    
    def natural_key(self):
        return (self.name,)


class ApiAccessManager(models.Manager):
    def get_by_natural_key(self, community_name, level_name):
        return self.get(
            community__name=community_name,
            level__name=level_name,
        )


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
    reply_count = models.BooleanField(
        default=False,
        verbose_name=_('Reply count'),
        help_text=_("Access status reply count."),
    )
    filter_author_self = models.BooleanField(
        default=False,
        verbose_name=_('Filter author self'),
        help_text=_("Filter status by authenticated author."),
    )
    search_engine = models.BooleanField(
        default=False,
        verbose_name=_('Search engine'),
        help_text=_("Search engine."),
    )

    objects = ApiAccessManager()

    def __str__(self):
        return f"API Access: community = {self.community} ; level = {self.level}"


    class Meta:
        unique_together = ("community", "level")

    def natural_key(self):
        return (self.community.natural_key() + self.level.natural_key())


class BlogManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Blog(models.Model):
    name = models.CharField(
        max_length=254,
        help_text=_("Name of the blog."),
        unique=True,
    )
    link = models.CharField(
        max_length=254,
        help_text=_("Link text."),
    )
    url = models.URLField()
    
    objects = BlogManager()

    def __str__(self):
        return f"{self.name} <{self.url}>"

    def natural_key(self):
        return (self.name,)