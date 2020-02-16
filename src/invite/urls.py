from django.urls import include, path
from django.views.generic import TemplateView
from . import views

app_name = 'invite'


urlpatterns = [
    path('invite/', views.invite, name='form'),
    path('thanks/', TemplateView.as_view(template_name='invite/thanks.html')),
]