from django.db import models
from django.contrib.sites.models import Site
import logging

logger = logging.getLogger(__name__)


class Community(models.Model):
    name = models.CharField(max_length=101, unique=True)
    active = models.BooleanField(default=False)
    account = models.OneToOneField(
        'bot.Account',
        on_delete=models.CASCADE
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
        on_delete=models.PROTECT,
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

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "communities"


def get_default_community():
    try:
        community = Community.objects.first()
        if community:
            return community.pk
    except Community.DoesNotExist as e:
        logger.debug("Create a default Community object with pk equal to one.", e)


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