from hcp.models import HealthCareProvider
from rest_framework import serializers

class HealthCareProviderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = HealthCareProvider
        depth=1
        fields = (
            'id',
            'human',
            'entity',
            'taxonomy',
            'created',
            'updated',
        )