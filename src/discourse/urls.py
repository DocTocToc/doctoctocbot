from django.urls import path

from discourse import views

app_name = 'discourse'

urlpatterns = [
    path('sso/', views.discourse_sso),
]