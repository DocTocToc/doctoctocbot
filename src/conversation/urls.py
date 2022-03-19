from django.urls import include, path
from rest_framework import routers

from . import views
from . import api_views

router = routers.DefaultRouter()
router.register(r'hashtags', views.HashtagViewSet)
router.register(r'tweets', api_views.TweetdjViewSet)

app_name = 'conversation'

urlpatterns = [
    #path('', views.show_conversations, name='conversations'),
    path('api/v1/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path("search/", views.SearchResultsList.as_view(), name="search_results"),
]