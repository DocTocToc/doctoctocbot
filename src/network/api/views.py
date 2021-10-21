import logging

from network.models import (
    Network,
)
from network.api import serializers
from rest_framework import viewsets
from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes,
    renderer_classes,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import bad_request, server_error
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)

@permission_classes([AllowAny])
class NetworkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing networks.
    """
    queryset = Network.objects.all()
    serializer_class = serializers.NetworkSerializer



