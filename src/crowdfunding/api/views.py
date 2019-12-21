import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render
from rest_framework import viewsets
from crowdfunding.models import ProjectInvestment
from crowdfunding.api.serializers import ProjectInvestmentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from dry_rest_permissions.generics import DRYPermissions
from dry_rest_permissions.generics import DRYPermissionFiltersBase
from django.views.generic import TemplateView
from django.utils.translation import gettext as _
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models import F
from django.db.utils import DatabaseError
from django.conf import settings
from django.core.paginator import Paginator
from community.helpers import get_community
from moderation.thumbnail import get_thumbnail_url
from django.contrib.sites.shortcuts import get_current_site
import logging

logger = logging.getLogger(__name__)


class ProjectInvestmentFilterBackend(DRYPermissionFiltersBase):
    action_routing = True

    def filter_list_queryset(self, request, queryset, view):
        """
        Limits all list requests to only be seen by the moderator.
        """
        return queryset.filter(
            user=request.user,
            paid=True
        ).order_by('datetime')


class ProjectInvestmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ProjectInvestment objects to be viewed.
    """
    permission_classes = (IsAuthenticated, DRYPermissions,)
    #permission_classes = (AllowAny, DRYPermissions,)
    queryset = ProjectInvestment.objects.all()
    serializer_class = ProjectInvestmentSerializer
    filter_backends = (ProjectInvestmentFilterBackend,)