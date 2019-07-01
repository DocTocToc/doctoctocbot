from django.shortcuts import render
from dry_rest_permissions.generics import DRYPermissions, DRYPermissionFiltersBase
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import HashtagSerializer
from .models import Hashtag

from .models import Treedj, Tweetdj


def show_conversations(request):
    return render(request, "conversation/status.html", {'treedj': Treedj.objects.all()})


class HashtagFilterBackend(DRYPermissionFiltersBase):
    action_routing = True


class HashtagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows hashtag objects to be viewed.
    """
    permission_classes = (IsAuthenticated, DRYPermissions,)
    #permission_classes = (AllowAny, DRYPermissions,)
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer