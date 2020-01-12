from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.urls import path

from discourse import views

app_name = 'discourse'

urlpatterns = [
    url(
        '^discourse/sso$',
        views.discourse_sso,
        name= 'discourse-sso'
    ),
    path(
        'discourse/unauthorized/',
        login_required(TemplateView.as_view(template_name="discourse/unauthorized.html")),
        name="discourse-unauthorized"
    ),
]