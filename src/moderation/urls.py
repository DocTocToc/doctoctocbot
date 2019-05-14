from django.urls import include, path
from rest_framework import routers
from moderation import views

router = routers.DefaultRouter()
router.register(r'moderators', views.ModeratorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]