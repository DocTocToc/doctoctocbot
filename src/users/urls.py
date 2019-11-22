from django.urls import path

from .views import settings, password

app_name = 'users'
    
urlpatterns = [   
    path('settings/', settings, name='settings'),
    path('settings/password/', password, name='password'),
]