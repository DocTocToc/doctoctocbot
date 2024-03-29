from moderation.models import (
    SocialUser,
    MastodonUser,
    Moderator,
    Category,
)
from moderation.api import serializers
from moderation.tasks import handle_create_twitter_socialuser

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.fields.json import KeyTransform
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.exceptions import bad_request, server_error
from dry_rest_permissions.generics import DRYPermissions
from dry_rest_permissions.generics import DRYPermissionFiltersBase
from community.helpers import get_community

class ModeratorFilterBackend(DRYPermissionFiltersBase):
    action_routing = True

    def filter_list_queryset(self, request, queryset, view):
        """
        Limits all list requests to only be seen by the moderator.
        """
        return queryset.filter(
            socialuser=request.user.socialuser,
            community=get_current_site(request).community,
        )


class ModeratorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows moderators objects to be viewed or edited.
    """
    permission_classes = (
        permissions.IsAuthenticated,
        DRYPermissions,
    )
    #permission_classes = (AllowAny, DRYPermissions,)
    queryset = Moderator.objects.all()
    serializer_class = serializers.ModeratorSerializer
    filter_backends = (ModeratorFilterBackend,)


class SocialUserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = SocialUser.objects.all() \
        .annotate(screen_name=KeyTransform('screen_name', 'profile__json'))
    serializer_class = serializers.SocialUserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        '=id',
        '=user_id',
        '=screen_name',
        
    ]
    if settings.DEBUG :
        permission_classes = [
            permissions.AllowAny
        ]
    else:
        permission_classes = [
            permissions.IsAdminUser
        ]


class CreateTwitterSocialUser(APIView):
    """
    View to create a new Twitter SocialUser.

    * Requires token authentication.
    * Only authenticated users are able to access this view.
    """
    if settings.DEBUG :
        permission_classes = [
            permissions.AllowAny
        ]
    else:
        permission_classes = [
            permissions.IsAdminUser
        ]

    def get(self, request, *args, **kwargs):
        screen_name: str = kwargs.get('screen_name', None)
        if not screen_name:
            return bad_request(request)
        try:
            username = request.user.username
        except:
            return bad_request(request)
        domain = request.site.domain
        community = get_community(request)
        bot_screen_name = community.account.username
        handle_create_twitter_socialuser(
            screen_name, username, domain, bot_screen_name
        )
        return Response(status=200)


class MastodonUserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = MastodonUser.objects.all()
    serializer_class = serializers.MastodonUserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        '=id',
        '=acct',
        
    ]
    if settings.DEBUG :
        permission_classes = [
            permissions.AllowAny
        ]
    else:
        permission_classes = [
            permissions.IsAdminUser
        ]
