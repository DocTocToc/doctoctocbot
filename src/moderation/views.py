import json
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.sites.models import Site
from rest_framework import viewsets
from .models import Moderator
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.views.generic import TemplateView
from django.utils.translation import gettext as _
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models import F
from django.db.utils import DatabaseError
from django.conf import settings
from community.helpers import (
    get_community,
    get_community_bot_screen_name,
    activate_language,
)
from moderation.thumbnail import get_thumbnail_url
from django.contrib.sites.shortcuts import get_current_site
import logging
from moderation.forms import SelfModerationForm
from social_django.models import UserSocialAuth
from moderation.models import UserCategoryRelationship
from django.core.mail import send_mail
from bot.tasks import handle_create_friendship
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils.translation import get_language

logger = logging.getLogger(__name__)

if settings.DEBUG:
    TIMEOUT = 1
else:
    TIMEOUT = 60 * 60


@method_decorator(cache_page(TIMEOUT), name='dispatch')
class ModeratorPublicList(TemplateView):
    title = _("Moderation team")
    template_name = "moderation/moderators.html"

    def get_context_data(self, *args, **kwargs):
        # Yield successive n-sized 
        # chunks from l. 
        def divide_chunks(l, n): 
            # looping till length l 
            for i in range(0, len(l), n):  
                yield l[i:i + n] 

        context = super(ModeratorPublicList, self).get_context_data(*args, **kwargs)
        community = get_community(self.request)
        if not community:
            return context
        moderators_qs = (
            Moderator.objects
            .filter(
                public=True,
                active=True,
                community=community
            )
            .annotate(
                screen_name=KeyTextTransform('screen_name', 'socialuser__profile__json'),
                name=KeyTextTransform('name', 'socialuser__profile__json'),
                user_id=KeyTextTransform('id', 'socialuser__profile__json'),
                avatar=F('socialuser__profile__biggeravatar')
            )
            .values(
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
        context["thumbnail"] = f"{self.request.scheme}://{self.request.get_host()}{get_thumbnail_url(community)}"
        try:
            twitter_creator = f"@{community.twitter_creator.screen_name_tag()}"
        except:
            twitter_creator = None
        context["twitter_creator"] = twitter_creator 
        return context


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def moderator_id_view(request):
        try:
            socialuser = request.user.socialuser
        except DatabaseError:
            return Response({"moderator_id": None})

        moderator = Moderator.objects.filter(
            socialuser=socialuser,
            community=get_current_site(request).community
            ).first()
        return Response({"id": moderator.id})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def follower_view(request):
        try:
            socialuser = request.user.socialuser
        except DatabaseError:
            return Response({"is_following": False})
        if True:
            return Response({"is_following": True})


class SelfModerationView(LoginRequiredMixin, FormView):
    template_name = 'moderation/self_moderation_form.html'
    form_class = SelfModerationForm

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(SelfModerationView, self).get_form_kwargs(*args, **kwargs)
        kwargs.update({'request': self.request})
        return kwargs

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # create moderation task here
        user = self.request.user
        if UserSocialAuth.objects.filter(
                provider='twitter',
                user=user,
            ).exists():
            category_name = form.cleaned_data['category']
            community = get_community(self.request)
            user.socialuser.self_moderate(
                category_name=category_name,
                community=community 
            )
            #apply_async(args=(status.id,), ignore_result=True)
            handle_create_friendship.apply_async(
                args = (
                    user.socialuser.user_id,
                    community.id,
                ),
                ignore_result=True,
            )
            #email
            scheme = self.request.is_secure() and "https" or "http"
            su_admin_link = (
                f'{scheme}://'
                f'{Site.objects.get_current().domain}'
                f'/silver/admin/moderation/socialuser/{user.socialuser.id}/change/'
            )
            try:
                send_mail(
                    ('Please moderate this user: '
                    f'{user.username} {user.socialuser.screen_name_tag()}'),
                    f'{su_admin_link}',
                    settings.ADMIN_EMAIL_ADDRESS,
                    [settings.ADMIN_EMAIL_ADDRESS],
                    fail_silently=False,
                )
            except:
                logger.error("Self moderation email error for {user.username}")
        else:
            pass
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        user = self.request.user
        try:
            ucr = UserCategoryRelationship.objects.filter(
                moderator=user.socialuser,
                social_user=user.socialuser
                ).latest()
        except UserCategoryRelationship.DoesNotExist:
            return '/oauth/login/twitter/?next=/moderation/self/'
        community = get_community(self.request)
        bot_screen_name = get_community_bot_screen_name(community)
        return reverse_lazy(
            'moderation:self-success',
            kwargs = {'screen_name': bot_screen_name}
        )
