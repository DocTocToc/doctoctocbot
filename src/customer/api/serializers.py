from rest_framework import serializers
from customer.models import Customer

class CustomerSerializer(serializers.ModelSerializer):


    class Meta:
        model = Customer
        fields = (
            'first_name',
            'last_name',
            'address_1',
            'country',
            'city',
            'zip_code',
        )