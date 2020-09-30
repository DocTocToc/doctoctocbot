import logging

from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.db.models import Q, DateTimeField

from rest_framework import viewsets, serializers
from rest_framework.permissions import AllowAny, IsAdminUser

from . import models
from . import serializers
from rest_framework.pagination import PageNumberPagination

from moderation.models import SocialUser
from tagging.models import Category, TagKeyword

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TweetdjViewSet(viewsets.ModelViewSet):
    queryset = models.Tweetdj.objects.all().order_by('-created_at')
    serializer_class = serializers.TweetdjSerializer
    pagination_class = StandardResultsSetPagination

    if settings.DEBUG:
        permission_classes = (AllowAny,)
    else:
        permission_classes = (IsAdminUser,)


    def get_queryset(self):
        qs = super().get_queryset()
        qs = self.filter_by_site(qs)

        # from_datetime
        req_from_datetime = self.request.query_params.getlist('from_datetime')
        logger.debug(f"{req_from_datetime=}")
        if req_from_datetime and len(req_from_datetime) == 1:
            qs = self.filter_by_from_datetime(qs, req_from_datetime[0])
            
        # to_datetime
        req_to_datetime = self.request.query_params.getlist('to_datetime')
        logger.debug(f"{req_to_datetime=}")
        if req_to_datetime and len(req_to_datetime) == 1:
            qs = self.filter_by_to_datetime(qs, req_to_datetime[0])
        
        req_tags = self.request.query_params.getlist('tag')
        logger.debug(f"params type: {type(req_tags)}\n params: {req_tags}")
        if req_tags:
            logger.debug(f"{req_tags=}")
            # convert to int
            req_tags = [int(tag) for tag in req_tags]
            logger.debug(f"{req_tags=}")
            # categories
            community = get_current_site(self.request).community.first()
            cat_ids = list(
                Category.objects.filter(
                    is_category=True,
                    community=community
                ).values_list('taggit_tag__id', flat=True)
            )
            # append 0 wich represents uncategorized
            if cat_ids:
                cat_ids.append(0)
            logger.debug(f"{cat_ids=}")
            set_req = set(req_tags)
            set_cat = set(cat_ids)
            req_inter_cat = list(set_req & set_cat)
            logger.debug(f"{req_inter_cat=}")
            if (req_inter_cat):
                qs = self.filter_by_categories(qs, req_inter_cat)
            #tags
            tag_ids = list(
                TagKeyword.objects.all().values_list('tag__id', flat=True)
            )
            logger.debug(f"{tag_ids=}")
            set_tag = set(tag_ids)
            req_inter_tag = list(set_req & set_tag)
            logger.debug(f"{req_inter_tag=}")
            if (req_inter_tag):
                qs = self.filter_by_tags(qs, req_inter_tag)

            # filter out tweets authored by protected accounts if requesting
            # user is not a member of the community
            user = self.request.user
            
        return qs


    def filter_by_protected(self, queryset):
        """ Filter out statuses authored by protected accounts
        """
        return queryset.filter(json__user__protected=False)

    def filter_by_site(self, queryset):
        try:
            userid = get_current_site(self.request).community.first().account.userid
            logger.debug(f"userid:{userid}")
        except:
            return queryset
        try:
            su = SocialUser.objects.get(user_id=userid)
        except SocialUser.DoesNotExist:
            return queryset
        return queryset.filter(retweeted_by=su)
    
    def filter_by_categories(self, queryset, cats):
        logger.debug(f"{queryset} {cats}")
        # 0 means uncategorized: Tweetdj objects without any category tag
        if '0' in cats:
            return queryset.filter( Q(tags__id__in=cats) | Q(tags=None) ).distinct()
        else:
            return queryset.filter(tags__id__in=cats).distinct()
        
    def filter_by_tags(self, queryset, tags):
        return queryset.filter(tags__id__in=tags).distinct()

    def filter_by_from_datetime(self, queryset, from_datetime):
        from_datetime = DateTimeField().to_python(from_datetime)
        return queryset.filter(created_at__gte=from_datetime)

    def filter_by_to_datetime(self, queryset, to_datetime):
        to_datetime = DateTimeField().to_python(to_datetime)
        return queryset.filter(created_at__lte=to_datetime)