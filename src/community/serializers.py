from rest_framework import serializers
#from django.contrib.auth.models import User
from community.models import ApiAccess

class ApiAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiAccess
        fields = '__all__'