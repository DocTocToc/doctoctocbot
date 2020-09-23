from django.urls import include, path
from rest_framework import routers

from . import api_views

router = routers.DefaultRouter()
router.register(r'categories', api_views.CategoryViewSet)
router.register(r'tags', api_views.TagKeywordViewSet)


app_name = 'tagging'

urlpatterns = [
    #path('', views.show_conversations, name='conversations'),
    path('api/v1/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
