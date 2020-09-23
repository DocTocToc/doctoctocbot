from rest_framework import serializers
from .models import Category, TagKeyword


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = (
            'tag',
            'summary',
            'taggit_tag',
        )


class TagKeywordSerializer(serializers.ModelSerializer):
    tag_name = serializers.StringRelatedField(many=False, source="tag")


    class Meta:
        model = TagKeyword
        fields = (
            'tag',
            'tag_name',
        )