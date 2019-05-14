from django.shortcuts import render
from rest_framework import viewsets
from .models import Moderator
from .serializers import ModeratorSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from dry_rest_permissions.generics import DRYPermissions
from dry_rest_permissions.generics import DRYPermissionFiltersBase

class ModeratorFilterBackend(DRYPermissionFiltersBase):
    action_routing = True

    def filter_list_queryset(self, request, queryset, view):
        """
        Limits all list requests to only be seen by the moderator.
        """
        return queryset.filter(socialuser=request.user.socialuser)

class ModeratorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows moderators objects to be viewed or edited.
    """
    #permission_classes = (IsAuthenticated, DRYPermissions,)
    permission_classes = (AllowAny, DRYPermissions,)
    queryset = Moderator.objects.all()
    serializer_class = ModeratorSerializer
    #filter_backends = (ModeratorFilterBackend,)
