from django.urls import include, path
from rest_framework import routers

from . import api_views

router = routers.DefaultRouter()
router.register(
    r'community/language',
    api_views.CommunityLanguageViewSet,
    basename='CommunityLanguage'
)

app_name = 'community'

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(
        'api/v1/user-api-access/',
        api_views.UserApiAccessView.as_view({'get': 'retrieve'}),
        name='user-api-access'
    ),
]