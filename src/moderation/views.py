from django.shortcuts import render
from rest_framework import viewsets
from .models import Moderator
from .serializers import ModeratorSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from dry_rest_permissions.generics import DRYPermissions
from dry_rest_permissions.generics import DRYPermissionFiltersBase
from django.views.generic import TemplateView
from django.utils.translation import gettext as _
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models import F
from django.conf import settings
from django.core.paginator import Paginator
from moderation.thumbnail import get_thumbnail_url
import logging

logger = logging.getLogger(__name__)

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


class ModeratorPublicList(TemplateView):
    title = _("Moderators")
    template_name = "moderation/moderators.html"

    def get_context_data(self, *args, **kwargs):
        # Yield successive n-sized 
        # chunks from l. 
        def divide_chunks(l, n): 
            # looping till length l 
            for i in range(0, len(l), n):  
                yield l[i:i + n] 
        
        context = super(ModeratorPublicList, self).get_context_data(*args, **kwargs)
        moderators_qs = (
            Moderator.objects.filter(public=True)
            .annotate(
                screen_name=KeyTextTransform('screen_name', 'socialuser__profile__json'),
                name=KeyTextTransform('name', 'socialuser__profile__json'),
                user_id=KeyTextTransform('id', 'socialuser__profile__json'),
                avatar=F('socialuser__profile__biggeravatar')
            ).values(
                'screen_name',
                'name',
                #'socialuser__profile__normalavatar'
                'avatar'
            )
        )
        media_url = settings.MEDIA_URL
        moderators = []
        for moderator in moderators_qs:
            moderator["avatar"] = media_url + moderator["avatar"]
            moderators.append(moderator)
            
        n = 3
        moderators = list(divide_chunks(moderators, n))    
        context["moderators"] = moderators
        context["thumbnail"] = f"{self.request.scheme}://{self.request.get_host()}{get_thumbnail_url()}"
        logger.debug(context)
        return context

