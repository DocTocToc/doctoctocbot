import logging
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from network.models import (
    Network,
)
from community.models import Community, Retweet
from moderation.models import SocialUser, MastodonUser
from bot.models import Account
from choice.utils import room_url
from constance import config
from urllib.parse import quote

logger = logging.getLogger(__name__)


class MastodonUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = MastodonUser
        fields = (
            'acct',
            'followers_count',
        )


class SocialUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialUser
        fields = (
            'screen_name_tag',
            'twitter_followers_count',
        )


class AccountSerializer(serializers.ModelSerializer):
    socialuser = SocialUserSerializer(read_only=True)

    class Meta:
        model = Account
        fields = (
            'id',
            'userid',
            'username',
            'socialuser',
            'launch',
        )
        depth = 2


class CommunitySerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)
    mastodon_account = MastodonUserSerializer(read_only=True)

    hashtag = serializers.SerializerMethodField()

    def get_hashtag(self, community):
        return Retweet.objects.filter(
            community=community,
            retweet=True,
        ).values_list('hashtag__hashtag', flat=True).distinct()


    class Meta:
        model = Community
        fields = [
            'id',
            'name',
            'account',
            'mastodon_account',
            'hashtag',
            'membership',
            'created',
            'site'
        ]
        depth = 2


class NetworkSerializer(serializers.ModelSerializer):
    community = CommunitySerializer(many=True, read_only=True)
    twitter_account = AccountSerializer(many=False, read_only=True)
    #community = serializers.SlugRelatedField(
    #    many=True,
    #    read_only=True,
    #    slug_field='name'
    # )


    class Meta:
        model = Network
        fields = (
            'id',
            'name',
            'label',
            'community',
            'twitter_account',
            'twitter_followers_count',
            'mastodon_followers_count',
        )
        depth = 4
