from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework import routers
from moderation import views
from moderation.api import views as apiviews
from django.contrib.auth.decorators import login_required

app_name = 'moderation'

router = routers.DefaultRouter()
router.register(r'moderators', apiviews.ModeratorViewSet)
router.register(r'socialuser', apiviews.SocialUserViewSet)


urlpatterns = [
    path(
        'api/',
        include(router.urls)
    ),
    path(
        'api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    ),
    path(
        'api/create-twitter-socialuser/<slug:screen_name>/',
        apiviews.CreateTwitterSocialUser.as_view(),
        name='create-twitter-socialuser'),
    path(
        'list/', views.ModeratorPublicList.as_view(),
        name='list'
    ),
    path(
        'api/moderator-id/',
        views.moderator_id_view, name='moderator-id'
    ),
    path(
        'self/',
        views.SelfModerationView.as_view(),
        name='self'
    ),
    path(
        'self/success/<str:screen_name>/',
        views.TemplateView.as_view(
            template_name='moderation/self_moderation_form_success.html'
        ),
        name='self-success'
    ),
    path(
        'user/',
        login_required(
            views.TemplateView.as_view(
                template_name='moderation/user.html'
            )
        ),
        name='user'
    ),
]