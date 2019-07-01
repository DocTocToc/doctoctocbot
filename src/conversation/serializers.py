from rest_framework import serializers
from .models import Hashtag

class HashtagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hashtag
        fields = ('hashtag',)