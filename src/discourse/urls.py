from django.urls import path

from discourse import views

app_name = 'discourse'

urlpatterns = [
    path('discourse/sso/', views.discourse_sso),
]