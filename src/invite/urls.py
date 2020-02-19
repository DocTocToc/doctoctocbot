from django.urls import include, path
from django.views.generic import TemplateView
from . import views

app_name = 'invite'


urlpatterns = [
    path(
        'send-invite/',
        views.SendCategoryInvite.as_view(),
        name='send-invite'),
    path(
        'invite/thanks/',
        TemplateView.as_view(template_name='invite/thanks.html'),
        name='invite-thanks' 
    ),
]