from django.db import models

class Network(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
    )
    label = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    community = models.ManyToManyField(
        'community.Community',
        through='NetworkCommunity',
        through_fields=('network', 'community')
    )
    twitter_account = models.ForeignKey(
        "bot.Account",
        on_delete=models.PROTECT,
        related_name="network",
        null=True,
        blank=True,
    )


class NetworkCommunity(models.Model):
    network = models.ForeignKey(
        'Network',
        on_delete=models.PROTECT,
        related_name="network_community"
    )
    community = models.ForeignKey(
        'community.Community',
        on_delete=models.PROTECT,
        related_name="community_network"
    )
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)
    active = models.BooleanField(
        default=True,
        help_text="Is this community still active in this network?"
    )
