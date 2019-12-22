import json
import uuid
from rest_framework.decorators import api_view, permission_classes, parser_classes, renderer_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException, PermissionDenied
from django.shortcuts import render
from rest_framework import viewsets
from customer.models import Customer
from customer.api.serializers import CustomerSerializer
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
from crowdfunding.models import ProjectInvestment
from customer.billing import create_silver_invoice
import logging

logger = logging.getLogger(__name__)


class CustomerFilterBackend(DRYPermissionFiltersBase):
    action_routing = True

    def filter_list_queryset(self, request, queryset, view):
        """
        Limits all list requests to only be seen by the current user.
        """
        return queryset.filter(
            user=request.user,
        )


class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Customer objects to be viewed.
    """
    permission_classes = (IsAuthenticated, DRYPermissions,)
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = (CustomerFilterBackend,)


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


@api_view(['POST'])
@parser_classes([JSONParser])
@permission_classes([IsAuthenticated])
def create_invoice(request, format=None):
    if request.method == 'POST':
        user = request.user
        uid_str = request.data.get("uuid", None)
        if not uid_str:
            return Response({"authorize": None})
        uid = uuid.UUID(uid_str)
        try:
            pi = ProjectInvestment.objects.get(uuid=uid)
        except ProjectInvestment.DoesNotExist:
            return Response({"authorize": None})
        if pi.user != user:
            raise PermissionDenied
        res = create_silver_invoice(uid)
        if not res:
            raise ServiceUnavailable
        response = Response(res)
        response["Access-Control-Allow-Origin"] = "*"
        return response