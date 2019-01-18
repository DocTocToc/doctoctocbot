from django.urls import path
from django.views.decorators.cache import cache_page
from display.views import All
from django.views.generic import TemplateView

from . import views

app_name = 'landing'

urlpatterns = [
    path('', cache_page(60 * 1)(All.as_view()), name='index'),
    path('user/', views.UserInfo.as_view(), name='user'),
    path('crowdfunding/', TemplateView.as_view(template_name="landing/crowdfunding.html")),
    path('status/<int:statusid>/', views.status),
]
