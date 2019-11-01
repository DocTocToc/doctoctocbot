from django.urls import include, path
from rest_framework import routers
from moderation import views

app_name = 'moderation'

router = routers.DefaultRouter()
router.register(r'moderators', views.ModeratorViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('list/', views.ModeratorPublicList.as_view(), name='list'),
    path('api/moderator-id/', views.moderator_id_view, name='moderator-id')
]