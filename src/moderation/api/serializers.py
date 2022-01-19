from rest_framework import serializers
from moderation.models import (
    SocialUser,
    Moderator,
    Profile,
    Category,
    Human,
)

class ModeratorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Moderator
        fields = ('socialuser', 'active', 'public',)


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = (
            'id',
            'json',
            'created',
            'updated',
        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'label',
        )


class HumanSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Human
        fields = (
            'id',
            'created',
        )


class SocialUserSerializer(serializers.ModelSerializer):
    category= CategorySerializer
    profile = ProfileSerializer
    human = HumanSerializer(source='human_set', many=True, read_only=True)

    class Meta:
        model = SocialUser
        fields = (
            'id',
            'user_id',
            'category',
            'active',
            'profile',
            'human',
        )
        depth=1
        