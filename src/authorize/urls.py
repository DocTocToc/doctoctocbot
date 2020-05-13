from django.urls import include, path, re_path
from django.views.generic import TemplateView

from authorize import views

app_name = 'authorize'

urlpatterns = [
    path('', views.Request.as_view(), name='request'),
    path('callback/', views.Callback, name='callback'),
    path('success/', TemplateView.as_view(template_name='authorize/success.html'), name='success'),
]
