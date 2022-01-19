from django.urls import include, path
from rest_framework import routers
from network.api import views as api_views
from network import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.contrib.sites.models import Site

app_name = 'network'
current_site = Site.objects.get_current()

router = routers.DefaultRouter()
router.register(r'network', api_views.NetworkViewSet)

urlpatterns = [
    path(
        'api/',
        include(router.urls)
    ),
    path(
        '',
        views.NetworkView.as_view(),
        name='home'
    ),
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=staticfiles_storage.url(
                f'favicon/{current_site.domain}/favicon.ico'
            )
        )
    ),
]

# Use static() to add url mappings to serve static files during development (only)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)