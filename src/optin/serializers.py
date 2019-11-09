from rest_framework import serializers

from optin.models import OptIn, Option 


class OptInSerializer(serializers.Serializer):
    authorize = serializers.BooleanField(required=True)
    option = serializers.CharField(required=True, max_length=255)
    
    def update(self, instance, validated_data):
        instance.option = Option.objects.get(name=validated_data.get('option', instance.option))
        instance.socialuser = self.context['request'].user.socialuser
        instance.authorize = validated_data.get('authorize', instance.authorize)
        
    def validate_option(self, value):
        """
        Check that the option exists.
        """
        try:
            Option.objects.get(name=value)
        except Option.DoesNotExist:
            raise serializers.ValidationError("This opt-in option does not exist.")
        return value
    
    def validate(self, data):
        """
        Check that there is a socialuser associated with the user.
        """
        socialuser = self.context['request'].user.socialuser
        if not socialuser:
            raise serializers.ValidationError("This user is not associated with a SocialUser.")
        return data