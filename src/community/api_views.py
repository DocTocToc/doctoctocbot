from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site

from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from community.helpers import get_community
from community.models import ApiAccess, Community
from community.serializers import (
    ApiAccessSerializer,
    CommunityLanguageSerializer
)
from users.utils import get_api_level


class UserApiAccessView(viewsets.ModelViewSet):
    queryset = ApiAccess.objects.all()
    serializer_class = ApiAccessSerializer
    permission_classes = [AllowAny]
    # Cache requested url for each user for 2 hours
    #@method_decorator(cache_page(60*60*24))
    #@method_decorator(vary_on_cookie)
    def retrieve(self, request):
        community = get_community(request)
        user = request.user
        level = get_api_level(user, community)
        try:
            api_access = ApiAccess.objects.get(
                community=community,
                level=level,
            )
        except ApiAccess.DoesNotExist:
            return Response(data={"message": "No corresponding ApiAccess in DB"})
        serializer = ApiAccessSerializer(api_access)
        return Response(data=serializer.data)


class CommunityLanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunityLanguageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            id=get_current_site(self.request).community.id,
        )

"""
class UserApiAccessView(GenericAPIView):
    queryset = ApiAccess.objects.all()
    serializer_class = ApiAccessSerializer
    permission_classes = [AllowAny]
    # Cache requested url for each user for 2 hours
    #@method_decorator(cache_page(60*60*24))
    #@method_decorator(vary_on_cookie)
    def get(self, request, format=None):
        context = {}
        community = get_community(self.request)
        user = self.request.user
        level = get_api_level(user, community)
        try:
            api_access = ApiAccess.objects.get(
                community=community,
                level=level,
            )
        except ApiAccess.DoesNotExist:
            return Response(data={"message": "No corresponding ApiAccess in DB"})
        serializer = ApiAccessSerializer(api_access)
        context['user_api_access'] = serializer.data
        return Response(context, status=200)
"""