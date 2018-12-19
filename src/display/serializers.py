from .models import WebTweet
from rest_framework import serializers

class WebTweetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WebTweet
        fields = ('statusid', 'username', 'name', 'time', 'text', 'html', 'like', 'retweet', 'reply')