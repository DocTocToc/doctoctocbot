from rest_framework import serializers
from .models import Hashtag, Tweetdj
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from display.views import (
    get_biggeravatar_url,
    get_normalavatar_url,
    get_miniavatar_url,
)


class HashtagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hashtag
        fields = ('hashtag',)
        

class TweetdjSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    avatar_normal = serializers.SerializerMethodField()
    avatar_mini = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_screen_name = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    id_str = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()

    
    class Meta:
        model = Tweetdj
        fields = (
            'statusid',
            'id_str',
            'userid',
            'socialuser',
            'user_name',
            'user_screen_name',
            'created_at',
            'text',
            'tags',
            'avatar_normal',
            'avatar_mini',
        )

    def get_id_str(self, obj):
        try:
            return obj.json['id_str']
        except TypeError:
            return ""

    def get_avatar_normal(self, obj):
        return get_normalavatar_url(obj.userid)
    
    def get_avatar_mini(self, obj):
        return get_miniavatar_url(obj.userid)
    
    def get_user_name(self, obj):
        try:
            return obj.json['user']['name']
        except TypeError:
            return ""

    def get_user_screen_name(self, obj):
        try:
            return obj.json['user']['screen_name']
        except TypeError:
            return ""

    def get_created_at(self, obj):
        try:
            return obj.json['created_at']
        except TypeError:
            return ""

    def get_text(self, obj):
        try:
            return obj.json['full_text']
        except TypeError:
            try:
                return obj.json['text']
            except TypeError:
                return ""