from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'hashtags', views.HashtagViewSet)

app_name = 'conversation'

urlpatterns = [
    #path('', views.show_conversations, name='conversations'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]