from rest_framework import serializers
from moderation.models import SocialUser, Moderator, Profile, Category

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


class SocialUserSerializer(serializers.ModelSerializer):
    category= CategorySerializer
    profile = ProfileSerializer

    class Meta:
        model = SocialUser
        fields = (
            'id',
            'user_id',
            'category',
            'active',
            'profile',
        )
        depth=1
        