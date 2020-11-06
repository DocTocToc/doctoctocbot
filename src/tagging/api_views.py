import logging

from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from rest_framework import viewsets, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated

from . import models
from . import serializers
from rest_framework.pagination import PageNumberPagination

from moderation.models import SocialUser

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    pagination_class = StandardResultsSetPagination
    if settings.DEBUG:
        permission_classes = (AllowAny,)
    #permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(is_category=True)
        qs = self.filter_by_site(qs)
        return qs
    
    def filter_by_site(self, queryset):
        try:
            community = get_current_site(self.request).community.first()
            logger.debug(f"{community=}")
        except:
            return queryset
        return queryset.filter(community=community)


class TagKeywordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.TagKeyword.objects.all()
    serializer_class = serializers.TagKeywordSerializer
    pagination_class = StandardResultsSetPagination
    if settings.DEBUG:
        permission_classes = (AllowAny,)
    #permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = self.filter_by_site(qs)
        return qs

    def filter_by_site(self, queryset):
        try:
            community = get_current_site(self.request).community.first()
            logger.debug(f"{community=}")
        except:
            return queryset
        return queryset.filter(community=community)