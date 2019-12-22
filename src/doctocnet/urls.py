"""doctocnet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
# wagtail start
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.core import urls as wagtail_urls
# wagtail stop
from ajax_select import urls as ajax_select_urls
from doctocnet.views import media_access

urlpatterns = [
    re_path(r'^media/(?P<path>.*)', media_access, name='media'),
    path('admin/', admin.site.urls),
    path('silver/', include('silver.urls')),
    path('optin/', include('optin.urls')),
    path('moderation/', include('moderation.urls')),
    path('', include('landing.urls')),
    path('', include('users.urls')),
    path('', include('registration.urls')),
    path('', include('customer.urls')),
    path('', include('gpgcontact.urls')),
    path('', include('discourse.urls')),
    path('financement/', include('crowdfunding.urls')),
    path('display/', include('display.urls', namespace='display')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),

    path('conversation/', include('conversation.urls')),
    re_path(r'^ajax_select/', include(ajax_select_urls)),
    path('crowd/', TemplateView.as_view(template_name='base.html')),
    path('charts/', include('charts.urls', namespace='charts')),
    
    # wagtail
    re_path(r'^cms/', include(wagtailadmin_urls)),
    re_path(r'^documents/', include(wagtaildocs_urls)),
#    re_path(r'^pages/', include(wagtail_urls)),
    re_path(r'', include(wagtail_urls)),
]

# Use static() to add url mappings to serve static files during development (only)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)