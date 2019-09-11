from django.conf.urls import url

from discourse import views

app_name = 'discourse'

urlpatterns = [
    url(
        '^discourse/sso$',
        views.discourse_sso,
        name= 'discourse-sso'
    ),
]