from django.urls import path
from django.conf.urls import url, include
from django.views.decorators.cache import cache_page

from .models import WebTweet
from .serializers import WebTweetSerializer
from rest_framework import routers, viewsets

from . import views

app_name = 'display'

# ViewSets define the view behavior.
class WebTweetViewSet(viewsets.ModelViewSet):
    queryset = WebTweet.objects.all()
    serializer_class = WebTweetSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'webtweet', WebTweetViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('status/<int:statusid>/', views.Status.as_view()),
    path('status/last/', cache_page(60 * 1)(views.Last.as_view())),
    path('status/top/', cache_page(60 * 1)(views.Top.as_view())),
    path('status/help/', cache_page(60 * 1)(views.Help.as_view())),
    path('status/all/', cache_page(60 * 1)(views.All.as_view())),
]