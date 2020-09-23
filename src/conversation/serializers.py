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
    json = serializers.JSONField()
    tags = TagListSerializerField()
    avatar_normal = serializers.SerializerMethodField()
    avatar_mini = serializers.SerializerMethodField()

    class Meta:
        model = Tweetdj
        fields = (
            'statusid',
            'userid',
            'socialuser',
            'json',
            'tags',
            'avatar_normal',
            'avatar_mini',
        )
        
    def get_avatar_normal(self, obj):
        return get_normalavatar_url(obj.userid)
    
    def get_avatar_mini(self, obj):
        return get_miniavatar_url(obj.userid)