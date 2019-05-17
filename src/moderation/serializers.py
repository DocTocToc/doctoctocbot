from rest_framework import serializers
from .models import Moderator

class ModeratorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Moderator
        fields = ('socialuser', 'active', 'public',)