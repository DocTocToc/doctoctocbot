from community.helpers import get_community
from django.contrib.sites.shortcuts import get_current_site
from users.utils import get_twitter_social_user, get_local_social_user
from moderation.models import UserCategoryRelationship
from hcp.models import HealthCareProvider
from conversation.models import SearchLog
from django.db import DatabaseError
import logging

logger = logging.getLogger(__name__)

class SearchLogger():

    def __init__(self, request):
        self.request = request
        self.user = self.request.user
        self.site = get_current_site(request)
        self.query_parameters = request.query_params
        self.categories = self.get_user_categories()
        self.taxonomies = self.get_user_taxonomies()

    def get_social_user(self):
        return (
            get_twitter_social_user(self.user) or
            get_local_social_user(self.user)
        )

    def get_user_categories(self):
        if not self.user.is_authenticated:
            return
        su = self.get_social_user()
        if su:
            return (
                UserCategoryRelationship.objects.filter(social_user=su)
                .values_list('category__id', flat=True)
            )

    def get_user_taxonomies(self):
        if not self.user.is_authenticated:
            return
        su = self.get_social_user()
        try:
            return (
                HealthCareProvider.objects.filter(human__in=su.human_set.all())
                .values_list('taxonomy__id', flat=True)
            )
        except AttributeError:
            return

    def log(self):
        try:
            sl = SearchLog.objects.create(
                query_parameters = self.query_parameters,
                site = self.site
            )
            try:
                sl.categories.add(* self.get_user_categories())
                sl.taxonomies.add(* self.get_user_taxonomies())
            except TypeError:
                pass
        except DatabaseError as e:
            logger.error(e)
