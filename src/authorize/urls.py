from authorize import views
from django.urls import include, path, re_path
from django.views.generic import TemplateView


app_name = 'authorize'

urlpatterns = [
    path('<app_name>', views.Request.as_view(), name='request'),
    path('callback/', views.Callback, name='callback'),
    path('success/', TemplateView.as_view(template_name='authorize/success.html'), name='success'),
    path('error/', TemplateView.as_view(template_name='authorize/error.html'), name='error'),
]
