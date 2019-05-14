from rest_framework import serializers
from .models import Moderator

class ModeratorSerializer(serializers.ModelSerializer):
    #socialuser = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    #socialuser = serializers.StringRelatedField(many=False)

    class Meta:
        model = Moderator
        fields = ('socialuser', 'active',)
        #view_name='Moderators'