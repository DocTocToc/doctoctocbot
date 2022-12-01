from hcp.models import HealthCareProvider
from hcp.api import serializers

from django.conf import settings

from rest_framework.views import APIView
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.exceptions import bad_request, server_error
from dry_rest_permissions.generics import DRYPermissions
from dry_rest_permissions.generics import DRYPermissionFiltersBase
from django_filters.rest_framework import DjangoFilterBackend



class HealthCareProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    """
    queryset = HealthCareProvider.objects.all()
    serializer_class = serializers.HealthCareProviderSerializer
    filter_backends = [
        #filters.SearchFilter,
        DjangoFilterBackend
    ]
    #search_fields = (
    #    'human__id',        
    #)
    filterset_fields = [
        'human__id',
        'entity__id',      
    ]
    if settings.DEBUG :
        permission_classes = [
            permissions.AllowAny
        ]
    else:
        permission_classes = [
            permissions.IsAdminUser
        ]