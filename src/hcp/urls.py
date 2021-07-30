from django.urls import include, path
from rest_framework import routers
from hcp.api import views as apiviews
from django.contrib.auth.decorators import login_required

app_name = 'hcp'

router = routers.DefaultRouter()
router.register(r'hcp', apiviews.HealthCareProviderViewSet)


urlpatterns = [
    path(
        'api/',
        include(router.urls)
    ),
    path(
        'api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    ),
]