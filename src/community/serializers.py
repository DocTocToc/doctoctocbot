from rest_framework import serializers
#from django.contrib.auth.models import User
from community.models import ApiAccess, Community
from langcodes import *
import logging

logger = logging.getLogger(__name__)

class ApiAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiAccess
        fields = '__all__'


class CommunityLanguageSerializer(serializers.ModelSerializer):
    language_name = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = ['id', 'name', 'language', 'language_name']
        
    def get_language_name(self, obj):
        iso_code =  obj.language
        logger.debug(f'{iso_code=}')
        language_name = Language.get(iso_code).display_name(iso_code)
        logger.debug(f'{language_name=}')
        return language_name