from rest_framework import serializers
from moderation.models import (
    SocialUser,
    MastodonUser,
    Moderator,
    Profile,
    Category,
    Human,
    UserCategoryRelationship,
)

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = (
            'id',
            'json',
            'created',
            'updated',
        )


class HumanSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Human
        fields = (
            'id',
            'created',
        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'label',
        )


class SocialUserSerializer2(serializers.ModelSerializer):
    profile = ProfileSerializer

    class Meta:
        model = SocialUser
        fields = (
            'id',
            'user_id',
            'profile',
        )
        depth=1


class UserCategoryRelationshipSerializer(serializers.ModelSerializer):
    social_user = SocialUserSerializer2(
        many=False,
        read_only=True
    )
    moderator = SocialUserSerializer2(
        many=False,
        read_only=True
    )

    class Meta:
        model = UserCategoryRelationship
        fields = (
            'social_user',
            'category',
            'moderator',
            'community',
            'created',
            'updated',
        )
        depth=2


class SocialUserSerializer(serializers.ModelSerializer):
    category= CategorySerializer
    profile = ProfileSerializer
    human = HumanSerializer(source='human_set', many=True, read_only=True)
    categoryrelationships = UserCategoryRelationshipSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = SocialUser
        fields = (
            'id',
            'user_id',
            'category',
            'active',
            'profile',
            'human',
            'entity',
            'categoryrelationships',
        )
        depth=1


class MastodonUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MastodonUser
        fields = (
            'id',
            'acct',
        )
        depth=1


class ModeratorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Moderator
        fields = ('socialuser', 'active', 'public',)