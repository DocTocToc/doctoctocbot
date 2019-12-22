from rest_framework import serializers
from crowdfunding.models import ProjectInvestment

class ProjectInvestmentSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='name'
    )


    class Meta:
        model = ProjectInvestment
        fields = ('pk', 'project', 'pledged', 'datetime', 'invoice', 'invoice_pdf',)