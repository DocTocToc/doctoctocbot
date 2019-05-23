from django.urls import path
from django.views.decorators.cache import cache_page
from display.views import All
from django.views.generic import TemplateView

from . import views

app_name = 'landing'

urlpatterns = [
    path('', All.as_view(), name='index'),
    path('user/', views.UserInfo.as_view(), name='user'),
    path('status/<int:statusid>/', views.status),
    
    path('privacy/', TemplateView.as_view(template_name='landing/privacy/index.html'), name='privacy'),
    path('about/', TemplateView.as_view(template_name='landing/about/index.html'), name='about'),
    path('license/', TemplateView.as_view(template_name='landing/license/index.html'), name='license'),
    path('rules/', TemplateView.as_view(template_name='landing/rules/index.html'), name='rules'),
    path('values/', TemplateView.as_view(template_name='landing/values/index.html'), name='values'),
    path('guidelines/', TemplateView.as_view(template_name='landing/guidelines/index.html'), name='guidelines'),
    path('moderation/', TemplateView.as_view(template_name='landing/moderation/index.html'), name='moderation'),
    path('moderation/moderator', TemplateView.as_view(template_name='landing/moderator/index.html'), name='moderator'),
    path('faq/', TemplateView.as_view(template_name='landing/faq/index.html'), name='faq'),

]
