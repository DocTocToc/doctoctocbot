import logging
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from network.models import Network
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes,
    renderer_classes,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from network.api.serializers import NetworkSerializer
from django.contrib.sites.models import Site
from network.api.serializers import NetworkSerializer

logger = logging.getLogger(__name__)

@permission_classes([AllowAny])
class NetworkView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'network/network.html'

    @method_decorator(cache_page(60*10))
    def get(self, request):
        network = Network.objects.filter(site=request.site).first()
        data = NetworkSerializer(network).data
        return Response({'network': data})