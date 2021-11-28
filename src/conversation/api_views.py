import logging

from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.db.models import Q, DateTimeField

from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from . import models
from rest_framework.pagination import PageNumberPagination

from community.helpers import get_community
from users.utils import get_api_level

from moderation.models import SocialUser
from tagging.models import Category, TagKeyword

from conversation.serializers import get_api_access, TweetdjSerializer

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class TweetdjViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Tweetdj.objects.all().order_by('-statusid')
    serializer_class = TweetdjSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (AllowAny,)


    def get_queryset(self):
        qs = super().get_queryset()
        qs = self.filter_by_site(qs)
        api_access = get_api_access(self.request)

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
        logger.debug(f"params type: {type(req_tags)}\n params: {req_tags=}")
        
        req_author = self.request.query_params.getlist('author')
        logger.debug(f"params type: {type(req_author)}\n params: {req_author=}")
        if req_author and req_author[0] == 'self':
            qs = self.filter_by_author_is_self(qs)

        if req_tags:
            logger.debug(f"{req_tags=}")
            # convert to int
            req_tags = [int(tag) for tag in req_tags]
            logger.debug(f"{req_tags=}")
            # categories
            community = get_current_site(self.request).community
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

        # filter out status authored by protected accounts if requesting
        # user is not a member of the community
        if (api_access and not api_access.status_protected):
            qs = self.filter_by_protected(qs)
        # status_limit: slice QuerySet if status_limit int is superior to 0
        if api_access and api_access.status_limit:
            qs = qs[:api_access.status_limit]
        return qs

    def filter_by_author_is_self(self, queryset):
        user = self.request.user
        if not user.is_authenticated:
            return queryset
        uids = [sa.uid for sa in user.social_auth.filter(provider='twitter')]
        logger.debug(f'{uids=}')
        if not uids:
            return queryset
        return queryset.filter(userid__in=uids)

    def filter_by_protected(self, queryset):
        """ Filter out statuses authored by protected accounts
        """
        return queryset.filter(json__user__protected=False)

    def filter_by_site(self, queryset):
        try:
            su = get_current_site(self.request).community.account.socialuser
        except:
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